from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from .models import Treinamentos
from django_q.models import Task
from .models import Pergunta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import DataTreinamento
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from django.conf import settings
from langchain_openai import ChatOpenAI
from pathlib import Path
from django.http import StreamingHttpResponse
from datetime import datetime


def treinar_ia(request):
    if request.method == "POST":
        site = request.POST.get("site")
        conteudo = request.POST.get("conteudo")
        documento = request.FILES.get("documento")

        if all([site, conteudo, documento]):
            treinamentos = Treinamentos(
                site=site, conteudo=conteudo, documento=documento
            )
            treinamentos.save()
            return redirect("treinar_ia")

    tasks = Task.objects.all()
        
    fontes = Treinamentos.objects.all()

    context = {
            "tasks": tasks,
            "fontes": fontes,
        }
        
    return render(request, "treinar_ia.html", context)



@csrf_exempt
def chat(request):
    horario_atual = datetime.now()

    if request.method == "GET":
        return render(request, "chat.html", {"horario_atual": horario_atual})
    elif request.method == "POST":
        pergunta_user = request.POST.get("pergunta")
        pergunta = Pergunta(pergunta=pergunta_user)
        pergunta.save()
        return JsonResponse({"id": pergunta.id})


@csrf_exempt
def stream_response(request):
    id_pergunta = request.POST.get("id_pergunta")
    pergunta = Pergunta.objects.get(id=id_pergunta)

    def stream_generator():
        embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
        vectordb = FAISS.load_local(
            "banco_faiss", embeddings, allow_dangerous_deserialization=True
        )

        docs = vectordb.similarity_search(pergunta.pergunta, k=5)
        for doc in docs:
            dt = DataTreinamento.objects.create(
                metadata=doc.metadata, texto=doc.page_content
            )
            pergunta.data_treinamento.add(dt)

        contexto = "\n\n".join(
            [
                f"Material: {Path(doc.metadata.get('source', 'Desconhecido')).name}\n{doc.page_content}"
                for doc in docs
            ]
        )

        messages = [
            {
                "role": "system",
                "content": f"Você é um assistente virtual e deve responder com precissão as perguntas sobre uma empresa.\n\n{contexto}",
            },
            {"role": "user", "content": pergunta.pergunta},
        ]

        llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            streaming=True,
            temperature=0,
            openai_api_key=settings.openai_api_key,
        )

        for chunk in llm.stream(messages):
            token = chunk.content
            if token:
                yield token

    return StreamingHttpResponse(
        stream_generator(), content_type="text/plain; charset=utf-8"
    )



def ver_fontes(request, id):
    pergunta = get_object_or_404(Pergunta, id=id)
    
    print(pergunta.data_treinamento)
    print(pergunta.pergunta)
    print("---")

    return render(request, "ver_fonte.html", {"pergunta": pergunta})