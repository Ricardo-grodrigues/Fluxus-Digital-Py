import hashlib

# Mantenha o MESMO segredo que está no seu software
SEGREDO_MESTRE = "FLUXUS_SISTEMA_PRIVADO_2024" 

def gerar_chave_para_cliente(id_pc):
    combinacao = (id_pc + SEGREDO_MESTRE).encode('utf-8')
    hash_completo = hashlib.sha256(combinacao).hexdigest()
    return hash_completo[:8].upper()

print("=== GERADOR DE CHAVES - FLUXUS DIGITAL ===")

while True:
    id_cliente = input("\nDigite o ID do PC do cliente (ou 'sair'): ").strip()
    
    if id_cliente.lower() == 'sair':
        break
        
    if id_cliente:
        chave = gerar_chave_para_cliente(id_cliente)
        print("\n" + "="*40)
        print(f"CHAVE DE ATIVAÇÃO: {chave}")
        print("="*40)
        print("\n(Pode copiar a chave acima e mandar para o cliente)")
    else:
        print("Erro: Digite um ID válido.")

input("\nPresione ENTER para fechar o gerador...")
