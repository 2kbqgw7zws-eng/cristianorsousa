import pandas as pd
import os
import django
import sys

# Configuração do ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from advocacia.models import DespesaAdvocacia

def importar():
    file_path = 'despesas.xlsx'
    if not os.path.exists(file_path):
        print(f"Erro: O arquivo '{file_path}' não foi encontrado!")
        return

    try:
        df = pd.read_excel(file_path)
        # Remove espaços e coloca tudo em minúsculo
        df.columns = df.columns.str.strip().str.lower()
        
        print(f"Colunas lidas: {list(df.columns)}")

        contador = 0
        for index, row in df.iterrows():
            # Busca a coluna 'descricao' OU 'descrição' OU 'descrição '
            descricao_final = ""
            for col in df.columns:
                if 'desc' in col:
                    descricao_final = row[col]
                    break
            
            # Busca a coluna 'data'
            data_final = row.get('data')
            # Busca a coluna 'local'
            local_final = row.get('local', '')
            # Busca a coluna 'valor'
            valor_final = row.get('valor')

            if pd.notnull(data_final) and pd.notnull(valor_final):
                DespesaAdvocacia.objects.create(
                    data=data_final,
                    descricao=descricao_final,
                    local=local_final,
                    valor=valor_final
                )
                contador += 1
        
        print(f"SUCESSO! {contador} despesas importadas.")

    except Exception as e:
        print(f"Erro detalhado: {e}")

if __name__ == "__main__":
    importar()