import assemblyai as aai
import os
from pydub import AudioSegment


aai.settings.api_key = "878f436a846942208a01746981fcf3cf"


aai.settings.http_timeout = 1200.0  


caminho_audio = r"C:\Users\matheusss\Downloads\Reunião.mp3"
caminho_comprimido = r"C:\Users\matheusss\Downloads\reuniao_temporaria_leve.mp3"
caminho_saida = r"C:\Users\matheusss\Downloads\transcricao_reuniao.txt"

print("Iniciando o processo...")

if not os.path.exists(caminho_audio):
    print(f"Erro: O arquivo final de áudio não foi encontrado em:\n{caminho_audio}")
    print("Verifique se o download no Opera já terminou de verdade!")
else:
    
    try:
        print("\nAnalisando e comprimindo o áudio da reunião...")
        audio = AudioSegment.from_file(caminho_audio)
        
       #conversão de audio 
        audio.export(caminho_comprimido, format="mp3", bitrate="32k", parameters=["-ac", "1"])
        print("Compressão concluída com sucesso!")
        audio_para_enviar = caminho_comprimido
    except Exception as e:
        print(f"Aviso: Não foi possível comprimir o áudio ({e}). Enviando o original...")
        audio_para_enviar = caminho_audio

    
    try:
        config = aai.TranscriptionConfig(
            speaker_labels=True, 
            language_code="pt"
        )

        transcritor = aai.Transcriber()
        
        print("\nEnviando o áudio da reunião para a AssemblyAI...")
        print("Processando vozes... Por favor, aguarde...")
        
        transcricao = transcritor.transcribe(audio_para_enviar, config=config)

        print("\nOrganizando as falas dos participantes...")
        with open(caminho_saida, "w", encoding="utf-8") as f:
            for fala in transcricao.utterances:
               #identificação por voz
                linha = f"Palestrante {fala.speaker}: {fala.text}\n\n"
                f.write(linha)

        print(f"\n--- Transcrição Concluída com Sucesso! ---")
        print(f"O roteiro da reunião foi salvo em:\n{caminho_saida}")

    except Exception as e:
        print(f"\nOcorreu um erro durante a transcrição: {e}")

    finally:
        # Remove o arquivo temporário
        if os.path.exists(caminho_comprimido):
            os.remove(caminho_comprimido)
            print("Limpeza concluída.")