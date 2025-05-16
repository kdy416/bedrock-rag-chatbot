
import os, sys, boto3
from variables import KNOWLEDGE_BASE_ID, FM_GENERATION_MODEL_ARN, MODEL_ARN, REGION

bedrock_agent_runtime_client = boto3.client("bedrock-agent-runtime", region_name=REGION)

# def query_knowledge_base(question):
def retrieve_context_from_kb(question):
    """Retriever: Knowledge Base에서 관련 문서 검색"""
    response = bedrock_agent_runtime_client.retrieve_and_generate(
        input={
            'text': question
        },
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': KNOWLEDGE_BASE_ID,
                'modelArn': MODEL_ARN,
                'retrievalConfiguration': {
                    'vectorSearchConfiguration': {
                        'overrideSearchType': 'HYBRID'
                    }
                }
            }
        },
    )
    # return response['output']['text']
    return response['citations'], response['output']['text']  # 문맥 + 초기 초안

# def query_foundation_model(prompts):
#     """
#     Step 2: Just call FM. (이전 code for type=MODEL)
#     'prompts' is the combined input or single string
#     """
def generate_answer_with_context(prompt):
    """Generator: 문맥 기반으로 최종 답변 생성"""
    response = bedrock_agent_runtime_client.retrieve_and_generate(
        # input={ 'text': prompts },
        input={ 'text': prompt },
        retrieveAndGenerateConfiguration={
            'type': 'EXTERNAL_SOURCES',
            'externalSourcesConfiguration': {
                'modelArn': FM_GENERATION_MODEL_ARN,  # e.g. anthropic.claude, ai21, TitanText
                'sources': [{'sourceType': 'BYTE_CONTENT', 'byteContent': ''}]
            }
        },
    )
    return response['output']['text']

def query_rag_plus_fm(question):
    # """
    # Hybrid approach:
    # 1) KB-based RAG => initial answer
    # 2) Then feed that answer (along with user Q) to a foundation model => refined final answer
    # """
    # # Step 1: retrieve from KB
    # rag_answer = query_knowledge_base(question)
    
    # # Compose final prompt for FM
    """Retriever + Generator 하이브리드 RAG 구조"""
    citations, rag_answer = retrieve_context_from_kb(question)

    final_prompt = f"""
User question:
{question}

# RAG-based draft answer:
RAG-based retrieved context summary:
{rag_answer}

Now refine the above answer with clear structure and any additional insights the foundation model can provide:
"""
    # Step 2: FM refine
    # final_answer = query_foundation_model(final_prompt)
    
    final_answer = generate_answer_with_context(final_prompt)

    return final_answer