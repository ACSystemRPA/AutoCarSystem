import httpx
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
import json
from app.extensions import db
from app.models import Configuracao
from app.modules.configuracoes import bp
from utils.auth import admin_ou_gerente


def get_config_valor(chave, default=None):
    config = Configuracao.query.filter_by(
        empresa_id=current_user.empresa_id, 
        chave=chave
    ).first()
    if config:
        return config.valor
    return default


def set_config_valor(chave, valor, tipo='string', descricao=''):
    config = Configuracao.query.filter_by(
        empresa_id=current_user.empresa_id, 
        chave=chave
    ).first()
    
    if config:
        config.valor = str(valor)
    else:
        config = Configuracao(
            empresa_id=current_user.empresa_id,
            chave=chave,
            valor=str(valor),
            tipo=tipo,
            descricao=descricao
        )
        db.session.add(config)
    db.session.commit()
    return config


@bp.route('/')
@login_required
@admin_ou_gerente
def index():
    geoapi_ativa = get_config_valor('geoapi_ativa', '1') == '1'
    return render_template('configuracoes/index.html', geoapi_ativa=geoapi_ativa)


@bp.route('/salvar', methods=['POST'])
@login_required
@admin_ou_gerente
def salvar():
    geoapi_ativa = '1' if request.form.get('geoapi_ativa') else '0'
    set_config_valor('geoapi_ativa', geoapi_ativa, 'bool', 'Ativa a busca automática de Códigos Postais (GeoAPI.pt)')
    flash('Configurações atualizadas com sucesso.', 'success')
    return redirect(url_for('configuracoes.index'))


@bp.route('/api/geo/codigo-postal/<cep>')
@login_required
def api_geo_codigo_postal(cep):
    # Proxy para evitar CORS e ocultar implementação interna.
    ativo = get_config_valor('geoapi_ativa', '1') == '1'
    
    if not ativo:
        return jsonify({"error": "Integração GeoAPI desativada pelas configurações da empresa."}), 403
        
    codigo_limpo = ''.join(c for c in cep if c.isdigit())
    if len(codigo_limpo) != 7:
        return jsonify({"error": "Formato de código postal inválido."}), 400
        
    codigo_formatado = f"{codigo_limpo[:4]}-{codigo_limpo[4:]}"
    url = f"https://json.geoapi.pt/codigo_postal/{codigo_formatado}"
    
    try:
        # Timeout de 5s para não travar a aplicação, client HTTP assíncrono seria ideal mas Síncrono simples já funciona no proxy.
        with httpx.Client(timeout=5.0) as client:
            response = client.get(url)
            
            if response.status_code == 200:
                dados = response.json()
                if "erro" in dados:
                    return jsonify({"error": "Código postal não encontrado na base GeoAPI."}), 404
                    
                # Mapeando resposta GeoAPI custom para a UI (normalmente retorna distritos, concelhos, localidades, e arruamentos limitados)
                # Formato típico GeoAPI array: 
                # [ { "Distrito": "Braga", "Concelho": "Viana do Castelo", "Localidade": "Viana", "Artéria": "Rua X", ...} ]
                # ou fallback seguro:
                return jsonify({"status": "success", "dados": dados})
            else:
                return jsonify({"error": f"Erro {response.status_code} na API remota."}), 502
    except httpx.RequestError as exc:
        return jsonify({"error": f"Erro de ligação à GeoAPI: {str(exc)}"}), 503
