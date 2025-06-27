from datetime import datetime
from decimal import Decimal, InvalidOperation
import re

class ContaBancaria:
    """Classe para gerenciar operações bancárias básicas"""
    
    def __init__(self, limite_saque=500, limite_saques_diarios=3):
        self.saldo = Decimal('0.00')
        self.limite_saque = Decimal(str(limite_saque))
        self.limite_saques_diarios = limite_saques_diarios
        self.numero_saques = 0
        self.historico = []
        
    def depositar(self, valor):
        """
        Realiza depósito na conta
        
        Args:
            valor (str/float): Valor a ser depositado
            
        Returns:
            tuple: (sucesso: bool, mensagem: str)
        """
        try:
            valor_decimal = self._validar_valor(valor)
            
            if valor_decimal <= 0:
                return False, "O valor deve ser positivo."
                
            self.saldo += valor_decimal
            self._adicionar_historico("DEPÓSITO", valor_decimal)
            
            return True, f"Depósito de R$ {valor_decimal:.2f} realizado com sucesso!"
            
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"
    
    def sacar(self, valor):
        """
        Realiza saque da conta
        
        Args:
            valor (str/float): Valor a ser sacado
            
        Returns:
            tuple: (sucesso: bool, mensagem: str)
        """
        try:
            valor_decimal = self._validar_valor(valor)
            
            if valor_decimal <= 0:
                return False, "O valor deve ser positivo."
                
            # Validações específicas do saque
            if self.numero_saques >= self.limite_saques_diarios:
                return False, f"Limite de {self.limite_saques_diarios} saques diários excedido."
                
            if valor_decimal > self.limite_saque:
                return False, f"Valor excede o limite de saque de R$ {self.limite_saque:.2f}."
                
            if valor_decimal > self.saldo:
                return False, f"Saldo insuficiente. Saldo atual: R$ {self.saldo:.2f}."
                
            # Realizar saque
            self.saldo -= valor_decimal
            self.numero_saques += 1
            self._adicionar_historico("SAQUE", valor_decimal)
            
            return True, f"Saque de R$ {valor_decimal:.2f} realizado com sucesso!"
            
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"
    
    def obter_extrato(self):
        """
        Gera extrato da conta
        
        Returns:
            str: Extrato formatado
        """
        linha_separadora = "=" * 50
        extrato = f"\n{linha_separadora}\n"
        extrato += f"{'EXTRATO BANCÁRIO':^50}\n"
        extrato += f"{linha_separadora}\n"
        
        if not self.historico:
            extrato += "Nenhuma movimentação realizada.\n"
        else:
            for operacao in self.historico:
                extrato += f"{operacao['data']} | {operacao['tipo']:>8} | R$ {operacao['valor']:>10.2f}\n"
        
        extrato += f"{linha_separadora}\n"
        extrato += f"SALDO ATUAL: R$ {self.saldo:>10.2f}\n"
        extrato += f"SAQUES REALIZADOS HOJE: {self.numero_saques}/{self.limite_saques_diarios}\n"
        extrato += f"{linha_separadora}\n"
        
        return extrato
    
    def _validar_valor(self, valor):
        """
        Valida e converte valor para Decimal
        
        Args:
            valor: Valor a ser validado
            
        Returns:
            Decimal: Valor validado
            
        Raises:
            ValueError: Se valor for inválido
        """
        if isinstance(valor, str):
            # Remove espaços e substitui vírgula por ponto
            valor = valor.strip().replace(',', '.')
            
            # Verifica se contém apenas números, ponto e vírgula
            if not re.match(r'^\d+(\.\d{1,2})?$', valor):
                raise ValueError("Formato de valor inválido. Use apenas números.")
        
        try:
            return Decimal(str(valor))
        except (InvalidOperation, TypeError):
            raise ValueError("Valor deve ser um número válido.")
    
    def _adicionar_historico(self, tipo, valor):
        """Adiciona operação ao histórico"""
        operacao = {
            'data': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'tipo': tipo,
            'valor': valor
        }
        self.historico.append(operacao)

class SistemaBancario:
    """Sistema principal para interação com o usuário"""
    
    def __init__(self):
        self.conta = ContaBancaria()
        self.menu_opcoes = {
            'd': ('Depositar', self._processar_deposito),
            's': ('Sacar', self._processar_saque),
            'e': ('Extrato', self._processar_extrato),
            'q': ('Sair', self._processar_saida)
        }
    
    def executar(self):
        """Loop principal do sistema"""
        print("=== BEM-VINDO AO SISTEMA BANCÁRIO ===\n")
        
        while True:
            try:
                opcao = self._exibir_menu()
                
                if opcao in self.menu_opcoes:
                    nome_opcao, funcao = self.menu_opcoes[opcao]
                    
                    if opcao == 'q':
                        if funcao():
                            break
                    else:
                        funcao()
                else:
                    print("❌ Opção inválida! Por favor, escolha uma opção válida.\n")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Operação cancelada pelo usuário. Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro inesperado: {e}\n")
    
    def _exibir_menu(self):
        """Exibe menu e retorna opção escolhida"""
        print("=" * 40)
        print("           MENU PRINCIPAL")
        print("=" * 40)
        
        for codigo, (nome, _) in self.menu_opcoes.items():
            emoji = self._obter_emoji(codigo)
            print(f"[{codigo.upper()}] {emoji} {nome}")
        
        print("=" * 40)
        return input("👉 Escolha uma opção: ").lower().strip()
    
    def _obter_emoji(self, codigo):
        """Retorna emoji para cada opção"""
        emojis = {'d': '💰', 's': '💸', 'e': '📄', 'q': '🚪'}
        return emojis.get(codigo, '📋')
    
    def _processar_deposito(self):
        """Processa operação de depósito"""
        print("\n💰 === DEPÓSITO ===")
        valor = input("💵 Digite o valor para depósito (ou Enter para cancelar): ").strip()
        
        if not valor:
            print("❌ Operação cancelada.\n")
            return
            
        sucesso, mensagem = self.conta.depositar(valor)
        
        if sucesso:
            print(f"✅ {mensagem}\n")
        else:
            print(f"❌ Erro: {mensagem}\n")
    
    def _processar_saque(self):
        """Processa operação de saque"""
        print("\n💸 === SAQUE ===")
        print(f"💡 Limite por saque: R$ {self.conta.limite_saque:.2f}")
        print(f"💡 Saques restantes hoje: {self.conta.limite_saques_diarios - self.conta.numero_saques}")
        
        valor = input("💵 Digite o valor para saque (ou Enter para cancelar): ").strip()
        
        if not valor:
            print("❌ Operação cancelada.\n")
            return
            
        sucesso, mensagem = self.conta.sacar(valor)
        
        if sucesso:
            print(f"✅ {mensagem}\n")
        else:
            print(f"❌ Erro: {mensagem}\n")
    
    def _processar_extrato(self):
        """Processa visualização do extrato"""
        print(self.conta.obter_extrato())
    
    def _processar_saida(self):
        """Processa saída do sistema"""
        print("\n👋 Obrigado por usar nosso sistema bancário!")
        print("🔒 Sessão encerrada com segurança.")
        return True

def main():
    """Função principal"""
    try:
        sistema = SistemaBancario()
        sistema.executar()
    except Exception as e:
        print(f"❌ Erro crítico do sistema: {e}")
        print("💡 Tente reiniciar o programa.")

if __name__ == "__main__":
    main()