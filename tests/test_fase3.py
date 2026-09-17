import unittest
import json
from datetime import datetime
from app import create_app, db
from app.models import Empresa, Usuario, Cliente, Veiculo, Peca, Servico, OrdemServico, ItemServico, ItemPeca

class Fase3TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret'
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Setup Empresa 1 (Alpha) e Empresa 2 (Beta)
        self.emp1 = Empresa(razao_social="Alpha Motors Ltda", nome_fantasia="Oficina Alpha Motors", nif="11.111.111/0001-11")
        db.session.add(self.emp1)
        db.session.flush()
        
        self.user1 = Usuario(empresa_id=self.emp1.id, nome="Carlos Alpha", email="carlos@alpha.com", papel="admin")
        self.user1.set_password("senha123")
        db.session.add(self.user1)

        self.mecanico1 = Usuario(empresa_id=self.emp1.id, nome="Mecânico João", email="joao.mecanico@alpha.com", papel="mecanico")
        self.mecanico1.set_password("senha123")
        db.session.add(self.mecanico1)

        self.cli1 = Cliente(empresa_id=self.emp1.id, nome="Marcos Souza", nif="111.222.333-44", telefone="11988887777")
        db.session.add(self.cli1)
        db.session.flush()

        self.veic1 = Veiculo(empresa_id=self.emp1.id, cliente_id=self.cli1.id, placa="ABC1D23", marca="Honda", modelo="Civic 2.0", ano_fabricacao=2020, ano_modelo=2021)
        db.session.add(self.veic1)

        self.peca1 = Peca(empresa_id=self.emp1.id, descricao="Óleo Motor 5W30 Sintético", codigo_referencia="OLEO-5W30", preco_custo=25.00, preco_venda=45.00, estoque_atual=20, estoque_minimo=5)
        self.peca2 = Peca(empresa_id=self.emp1.id, descricao="Filtro de Óleo", codigo_referencia="FIL-01", preco_custo=15.00, preco_venda=35.00, estoque_atual=10, estoque_minimo=2)
        db.session.add_all([self.peca1, self.peca2])

        self.serv1 = Servico(empresa_id=self.emp1.id, descricao="Troca de Óleo e Filtros", preco_padrao=80.00, tempo_estimado_minutos=30)
        self.serv2 = Servico(empresa_id=self.emp1.id, descricao="Alinhamento e Balanceamento 3D", preco_padrao=120.00, tempo_estimado_minutos=45)
        db.session.add_all([self.serv1, self.serv2])

        # Empresa 2
        self.emp2 = Empresa(razao_social="Beta Car Ltda", nome_fantasia="Oficina Beta Car", nif="22.222.222/0001-22")
        db.session.add(self.emp2)
        db.session.flush()
        
        self.user2 = Usuario(empresa_id=self.emp2.id, nome="Roberto Beta", email="roberto@beta.com", papel="admin")
        self.user2.set_password("senha123")
        db.session.add(self.user2)

        self.cli2 = Cliente(empresa_id=self.emp2.id, nome="Fernanda Lima", nif="999.888.777-66")
        db.session.add(self.cli2)
        db.session.flush()

        self.veic2 = Veiculo(empresa_id=self.emp2.id, cliente_id=self.cli2.id, placa="XYZ9K88", marca="Toyota", modelo="Corolla")
        db.session.add(self.veic2)
        
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        return self.client.post('/auth/login', data={'email': email, 'senha': password}, follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)

    def test_abertura_os_and_checklist(self):
        self.login('carlos@alpha.com', 'senha123')

        # Abertura de Nova OS com Checklist
        res = self.client.post('/os/nova', data={
            'cliente_id': self.cli1.id,
            'veiculo_id': self.veic1.id,
            'tipo': 'ORDEM_SERVICO',
            'km_atual': '45000',
            'nivel_combustivel': '1/2',
            'defeito_reclamado': 'Barulho na suspensão dianteira e revisão periódica',
            'diagnostico_tecnico': 'Necessidade de troca de óleo e checagem de freios',
            'data_previsao_entrega': '2025-10-30',
            'observacoes_internas': 'Cliente aguarda orçamento',
            'usuario_responsavel_id': self.mecanico1.id,
            'chk_estepe': 'on',
            'chk_macaco': 'on',
            'chk_chave_roda': 'on',
            'chk_triangulo': 'on',
            'chk_pertences': 'Óculos de sol no porta luvas'
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        self.assertIn('aberta com sucesso'.encode('utf-8'), res.data)

        # Verificar se foi persistido corretamente no banco
        os = OrdemServico.query.filter_by(empresa_id=self.emp1.id).first()
        self.assertIsNotNone(os)
        self.assertTrue(os.numero_os.startswith('OS-'))
        self.assertEqual(os.cliente_id, self.cli1.id)
        self.assertEqual(os.veiculo_id, self.veic1.id)
        self.assertEqual(os.km_atual, 45000)
        self.assertEqual(os.nivel_combustivel, '1/2')
        self.assertEqual(os.status, 'ABERTA')
        
        # Verificar checklist JSON
        chk = json.loads(os.checklist) if os.checklist else {}
        self.assertTrue(chk.get('estepe'))
        self.assertTrue(chk.get('macaco'))
        self.assertEqual(chk.get('pertences'), 'Óculos de sol no porta luvas')
        self.assertFalse(chk.get('documento'))

    def test_adicionar_itens_servico_e_pecas_e_totais(self):
        self.login('carlos@alpha.com', 'senha123')

        # Criar OS
        os = OrdemServico(
            empresa_id=self.emp1.id,
            numero_os="OS-2025-0001",
            cliente_id=self.cli1.id,
            veiculo_id=self.veic1.id,
            usuario_responsavel_id=self.user1.id,
            defeito_reclamado="Revisão de 50.000km"
        )
        db.session.add(os)
        db.session.commit()

        # 1. Adicionar Serviço 1 (Troca de Óleo - R$ 80,00, qtd: 1)
        res_serv = self.client.post(f'/os/{os.id}/adicionar-servico', data={
            'servico_id': self.serv1.id,
            'mecanico_id': self.mecanico1.id,
            'valor_unitario': '80.00',
            'quantidade': '1',
            'desconto': '0.00'
        }, follow_redirects=True)
        self.assertEqual(res_serv.status_code, 200)

        # 2. Adicionar Serviço 2 (Alinhamento - R$ 120,00, com R$ 20 de desconto = R$ 100,00)
        self.client.post(f'/os/{os.id}/adicionar-servico', data={
            'servico_id': self.serv2.id,
            'mecanico_id': self.mecanico1.id,
            'valor_unitario': '120.00',
            'quantidade': '1',
            'desconto': '20.00'
        }, follow_redirects=True)

        # 3. Adicionar Peça 1 (4 Litros de Óleo 5W30 a R$ 45,00 cada = R$ 180,00)
        res_peca = self.client.post(f'/os/{os.id}/adicionar-peca', data={
            'peca_id': self.peca1.id,
            'valor_unitario': '45.00',
            'quantidade': '4',
            'desconto': '0.00'
        }, follow_redirects=True)
        self.assertEqual(res_peca.status_code, 200)

        # 4. Adicionar Peça 2 (1 Filtro de Óleo a R$ 35,00)
        self.client.post(f'/os/{os.id}/adicionar-peca', data={
            'peca_id': self.peca2.id,
            'valor_unitario': '35.00',
            'quantidade': '1',
            'desconto': '0.00'
        }, follow_redirects=True)

        # Recarregar OS e validar totais
        db.session.refresh(os)
        # Serviços: 80.00 + 100.00 = 180.00
        self.assertEqual(os.valor_servicos, 180.00)
        # Peças: 180.00 + 35.00 = 215.00
        self.assertEqual(os.valor_pecas, 215.00)
        # Total: 180.00 + 215.00 = 395.00
        self.assertEqual(os.valor_total, 395.00)

        # Testar remoção de um item
        item_servico = os.itens_servicos[0]
        res_rem = self.client.post(f'/os/{os.id}/remover-servico/{item_servico.id}', follow_redirects=True)
        self.assertEqual(res_rem.status_code, 200)

        db.session.refresh(os)
        # Agora só tem o Alinhamento (100.00) + Peças (215.00) = 315.00
        self.assertEqual(os.valor_servicos, 100.00)
        self.assertEqual(os.valor_total, 315.00)

    def test_baixa_e_estorno_automatica_de_estoque(self):
        self.login('carlos@alpha.com', 'senha123')

        os = OrdemServico(
            empresa_id=self.emp1.id,
            numero_os="OS-2025-0002",
            cliente_id=self.cli1.id,
            veiculo_id=self.veic1.id,
            usuario_responsavel_id=self.user1.id,
            defeito_reclamado="Troca de óleo",
            status="EM_ANDAMENTO"
        )
        db.session.add(os)
        db.session.commit()

        # Adicionar 4 litros de óleo à OS (Estoque inicial: 20)
        self.client.post(f'/os/{os.id}/adicionar-peca', data={
            'peca_id': self.peca1.id,
            'valor_unitario': '45.00',
            'quantidade': '4',
            'desconto': '0.00'
        }, follow_redirects=True)

        # Verificar que antes de concluir o estoque ainda é 20
        db.session.refresh(self.peca1)
        self.assertEqual(self.peca1.estoque_atual, 20)

        # Mudar status para CONCLUIDA -> deve dar baixa de 4 unidades no estoque (20 - 4 = 16)
        res_status = self.client.post(f'/os/{os.id}/alterar-status', data={
            'status': 'CONCLUIDA'
        }, follow_redirects=True)
        self.assertEqual(res_status.status_code, 200)

        db.session.refresh(self.peca1)
        db.session.refresh(os)
        self.assertEqual(self.peca1.estoque_atual, 16)
        self.assertEqual(os.status, 'CONCLUIDA')
        self.assertIsNotNone(os.data_conclusao)

        # Mudar status para CANCELADA -> deve estornar as 4 unidades de volta ao estoque (16 + 4 = 20)
        self.client.post(f'/os/{os.id}/alterar-status', data={
            'status': 'CANCELADA'
        }, follow_redirects=True)

        db.session.refresh(self.peca1)
        db.session.refresh(os)
        self.assertEqual(self.peca1.estoque_atual, 20)
        self.assertEqual(os.status, 'CANCELADA')

    def test_multi_tenant_isolation(self):
        # Criar OS para Empresa 1
        os1 = OrdemServico(
            empresa_id=self.emp1.id,
            numero_os="OS-2025-0101",
            cliente_id=self.cli1.id,
            veiculo_id=self.veic1.id,
            usuario_responsavel_id=self.user1.id,
            defeito_reclamado="OS Privada Empresa 1"
        )
        db.session.add(os1)
        db.session.commit()

        # Login como Empresa 2 (Roberto Beta)
        self.login('roberto@beta.com', 'senha123')

        # 1. Tentar visualizar detalhes da OS da Empresa 1 -> Deve retornar 404
        res_get = self.client.get(f'/os/{os1.id}')
        self.assertEqual(res_get.status_code, 404)

        # 2. Tentar editar OS da Empresa 1 -> 404
        res_edit = self.client.post(f'/os/{os1.id}/editar', data={'defeito_reclamado': 'Hacked'}, follow_redirects=True)
        self.assertEqual(res_edit.status_code, 404)

        # 3. Tentar mudar status da OS da Empresa 1 -> 404
        res_status = self.client.post(f'/os/{os1.id}/alterar-status', data={'status': 'CANCELADA'}, follow_redirects=True)
        self.assertEqual(res_status.status_code, 404)

        # 4. Listagem de OS da Empresa 2 não deve conter a OS da Empresa 1
        res_list = self.client.get('/os/')
        self.assertEqual(res_list.status_code, 200)
        self.assertNotIn(b'OS Privada Empresa 1', res_list.data)

    def test_api_veiculos_cliente(self):
        self.login('carlos@alpha.com', 'senha123')

        # Buscar veículos do cliente 1 da empresa 1
        res = self.client.get(f'/os/api/veiculos-cliente/{self.cli1.id}')
        self.assertEqual(res.status_code, 200)
        dados = res.get_json()
        self.assertEqual(dados['status'], 'success')
        self.assertEqual(len(dados['veiculos']), 1)
        self.assertEqual(dados['veiculos'][0]['placa'], 'ABC1D23')

        # Tentar buscar veículos de um cliente de outra empresa (retorna 404 devido ao multi-tenant isolation)
        res_other = self.client.get(f'/os/api/veiculos-cliente/{self.cli2.id}')
        self.assertEqual(res_other.status_code, 404)

if __name__ == '__main__':
    unittest.main()
