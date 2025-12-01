"""
Script para excluir todos os pedidos (ServiceRequestModal)
Execute com: Get-Content delete_all_pedidos.py | python manage.py shell
"""

from services.models import ServiceRequestModal

print("=" * 60)
print("EXCLUSÃO DE TODOS OS PEDIDOS")
print("=" * 60)

# Contar pedidos antes da exclusão
total_antes = ServiceRequestModal.objects.all().count()
print(f"\nTotal de pedidos antes da exclusão: {total_antes}")

if total_antes > 0:
    # Confirmar exclusão
    print("\n⚠️  ATENÇÃO: Todos os pedidos serão excluídos!")
    
    # Excluir todos os pedidos
    ServiceRequestModal.objects.all().delete()
    
    # Verificar se foram excluídos
    total_depois = ServiceRequestModal.objects.all().count()
    print(f"\n✓ Pedidos excluídos com sucesso!")
    print(f"Total de pedidos após exclusão: {total_depois}")
else:
    print("\n✓ Não há pedidos para excluir.")

print("\n" + "=" * 60)
print("OPERAÇÃO CONCLUÍDA")
print("=" * 60)
