import pandas as pd
import os
import django
import sys

# 1. Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from advocacia.models import DespesaAdvocacia

def importar():
    file_path = 'despesas.xlsx'
    
    if not os.path.exists(file_path):
        print(f"Erro: O arquivo '{file_path}' não foi encontrado na raiz!")
        return

    print(f"Lendo arquivo {file_path}...")
    
    try:
        # Lê o Excel (ajusta formatos de data automaticamente)
        df = pd.read_excel(file_path)
        
        # Garante que os nomes das colunas estejam minúsculos para evitar erros
        df.columns = [c.lower().strip() for c in df.columns]
        
        contador = 0
        for index, row in df.iterrows():
            DespesaAdvocacia.objects.create(
                data=row['data'],
                descricao=row['descricao'],
                local=row['local'],
                valor=row['valor']
            )
            contador += 1
            
        print(f"Sucesso! {contador} despesas foram importadas para o banco de dados.")
        
    except Exception as e:
        print(f"Ocorreu um erro durante a importação: {e}")

if __name__ == "__main__":
    importar()