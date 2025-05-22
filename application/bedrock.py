
import os, sys, boto3
import base64
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
                'sources': [
                    {
                        'sourceType': 'BYTE_CONTENT',
                        'byteContent':{
                            'data': base64.b64encode(prompt.encode()).decode('utf-8'),
                            'contentType': 'text/plain',
                            'identifier': 'context-1'
                            }
                        }
                    ]
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
<system>
You are AWS Bedrock RAG assistant. 
• Write in concise Korean.  
• Never invent information that is not in the context.  
• Cite sources like [1], [2] right after the sentence that uses them.  
• Return **Markd
own** with at most three H2 sections: 📝Answer / 🔗Sources / 💡Follow-up.
</system>

<user_question>
{question}
</user_question>

<context>
{rag_answer}
</context>

<task>
Step 1 – Read <context>.  
Step 2 – Produce the 📝Answer section (≤ 200 tokens).  
Step 3 – List unique citations you actually used under 🔗Sources.  
Step 4 – Suggest one related question under 💡Follow-up.
</task>
"""
    # Step 2: FM refine
    # final_answer = query_foundation_model(final_prompt)
    
    final_prompt = build_final_prompt(question, rag_answer, citations)   # helper로 분리
    return generate_answer_with_context(final_prompt)