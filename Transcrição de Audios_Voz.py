import assemblyai as aai
import requests
import os

# CONFIGURAÇÕES
AQ_KEY = "KEY_DA_API_DO_GOOGLE"  # Substitua pelo seu API Key do Google
aai.settings.api_key = "KEY_DA_API_DO_ASSEMBLYAI"  # Substitua pelo seu API Key do AssemblyAI

caminho_audio = r"CAMINHO_DO_ARQUIVO_DE_AUDIO.mp3"  # Substitua pelo caminho do seu arquivo de áudio
caminho_saida = r"CAMINHO_DO_ARQUIVO_DE_SAIDA.txt"  # Substitua pelo caminho do seu arquivo de saída

def dividir_em_blocos(texto, caracteres_max=12000):
    paragrafos = texto.split('\n')
    blocos = []
    bloco_atual = ""
    for p in paragrafos:
        if len(bloco_atual) + len(p) < caracteres_max:
            bloco_atual += p + "\n"
        else:
            blocos.append(bloco_atual)
            bloco_atual = p + "\n"
    blocos.append(bloco_atual)
    return blocos

print("Iniciando processamento com Identificação Automática...")

try:
    transcritor = aai.Transcriber()
    config = aai.TranscriptionConfig(speaker_labels=True, language_code="pt")
    
    print("Transcrevendo...")
    transcricao = transcritor.transcribe(caminho_audio, config=config)
    texto_completo = "\n".join([f"Palestrante {f.speaker}: {f.text}" for f in transcricao.utterances])

    blocos = dividir_em_blocos(texto_completo)
    
    texto_final_revisado = ""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
    headers = {"x-goog-api-key": AQ_KEY, "Content-Type": "application/json"}

    for i, bloco in enumerate(blocos):
        print(f"-> Processando bloco {i+1}/{len(blocos)}...")
        
        # --- PROMPT INTELIGENTE ---
        comando = (
            "Analise o texto a seguir. "
            "1. IDENTIFICAÇÃO: É uma música, uma reunião de trabalho, uma palestra ou uma conversa informal? "
            "2. FORMATAÇÃO: "
            "   - Se for MÚSICA: Ignore os 'Palestrantes', remova tags de tempo, e estruture como letra (Versos, Refrão, Ponte). "
            "   - Se for REUNIÃO/CONVERSA: Mantenha os palestrantes, estruture como ata com tópicos e decisões. "
            "   - Se for PALESTRA: Formate com introdução, tópicos de desenvolvimento e conclusão. "
            "3. REGRA GERAL: Não resuma o conteúdo, mantenha as informações originais, corrija apenas gramática e ortografia. "
            "Texto:\n\n" + bloco
        )
        
        payload = {"contents": [{"parts": [{"text": comando}]}]}
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            texto_final_revisado += response.json()['candidates'][0]['content']['parts'][0]['text'] + "\n\n"
        else:
            print(f"Erro no bloco {i+1}: {response.text}")

    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(texto_final_revisado)
        
    print(f"\nSucesso! Arquivo final salvo em: {caminho_saida}")

except Exception as e:
    print(f"\nERRO: {e}")
