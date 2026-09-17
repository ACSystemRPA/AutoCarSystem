import io
import re
from urllib.parse import quote as url_quote

from flask import render_template, redirect, url_for, flash, request, send_file, abort, current_app
from flask_login import login_required, current_user

from xhtml2pdf import pisa

from app.extensions import db, mail
from app.models import OrdemServico
from app.modules.notificacoes import bp

from flask_mail import Message


def _buscar_os(id):
    return OrdemServico.query.filter_by(id=id, empresa_id=current_user.empresa_id).first_or_404()


def _telefone_limpo(telefone):
    if not telefone:
        return None
    return re.sub(r'\D', '', telefone)


def _texto_whatsapp(os):
    linhas = []
    empresa = os.empresa or current_user.empresa
    empresa_nome = empresa.nome_fantasia or empresa.razao_social
    linhas.append(f"*{os.numero_os} - {empresa_nome}*")
    linhas.append("")

    if os.cliente:
        linhas.append(f"*Cliente:* {os.cliente.nome}")
    if os.veiculo:
        veiculo = os.veiculo
        matricula = veiculo.matricula or ''
        modelo = veiculo.modelo or ''
        if matricula or modelo:
            linhas.append(f"*Viatura:* {modelo} ({matricula})".replace(' ()', ''))
    if os.km_atual:
        linhas.append(f"*KM atual:* {os.km_atual}")
    if os.defeito_reclamado:
        linhas.append(f"*Defeito reclamado:* {os.defeito_reclamado}")

    itens_servico = list(os.itens_servico)
    itens_peca = list(os.itens_peca)
    if itens_servico:
        linhas.append("")
        linhas.append("*Serviços:*")
        for item in itens_servico:
            qtd = f"{item.quantidade:g} x " if item.quantidade != 1.0 else ""
            linhas.append(f"{qtd}{item.descricao} - € {item.subtotal:.2f}")
    if itens_peca:
        linhas.append("")
        linhas.append("*Peças:*")
        for item in itens_peca:
            qtd = f"{item.quantidade:g} x " if item.quantidade != 1.0 else ""
            linhas.append(f"{qtd}{item.descricao} - € {item.subtotal:.2f}")

    linhas.append("")
    if os.valor_desconto > 0:
        linhas.append(f"*Desconto:* -€ {os.valor_desconto:.2f}")
    linhas.append(f"*Valor Total: € {os.valor_total:.2f}*")
    linhas.append("")
    linhas.append(f"*Status:* {os.status.replace('_', ' ').title()}")

    return "\n".join(linhas)


def gerar_pdf_os(os):
    """Gera o PDF da OS em memória e devolve (bytes, nome_arquivo)."""
    empresa = os.empresa or current_user.empresa
    html = render_template(
        'notificacoes/os_pdf.html',
        os=os,
        empresa=empresa,
        usuario=current_user
    )

    buffer = io.BytesIO()
    status = pisa.CreatePDF(src=html, dest=buffer, encoding='utf-8')
    if status.err:
        return None, None

    buffer.seek(0)
    nome_arquivo = f"OS-{os.numero_os}.pdf"
    return buffer, nome_arquivo


@bp.route('/os/<int:id>/pdf')
@login_required
def pdf(id):
    os = _buscar_os(id)
    buffer, nome_arquivo = gerar_pdf_os(os)
    if not buffer:
        flash('Não foi possível gerar o PDF desta Ordem de Serviço.', 'danger')
        return redirect(url_for('os.detalhes', id=os.id))
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=nome_arquivo
    )


@bp.route('/os/<int:id>/pdf/visualizar')
@login_required
def pdf_visualizar(id):
    os = _buscar_os(id)
    buffer, nome_arquivo = gerar_pdf_os(os)
    if not buffer:
        abort(500)
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=False,
        download_name=nome_arquivo
    )


@bp.route('/os/<int:id>/whatsapp')
@login_required
def whatsapp(id):
    os = _buscar_os(id)
    telefone = _telefone_limpo(os.cliente.telefone) if os.cliente else None
    if not telefone:
        flash('O cliente desta OS não possui telefone cadastrado para enviar via WhatsApp.', 'warning')
        return redirect(url_for('os.detalhes', id=os.id))

    texto = _texto_whatsapp(os)
    url = f"https://api.whatsapp.com/send?phone={telefone}&text={url_quote(texto)}"
    return redirect(url, code=302)


@bp.route('/os/<int:id>/enviar-email', methods=['POST'])
@login_required
def enviar_email(id):
    os = _buscar_os(id)

    if not os.cliente or not os.cliente.email:
        flash('O cliente desta OS não possui e-mail cadastrado.', 'warning')
        return redirect(url_for('os.detalhes', id=os.id))

    if not current_app.config.get('MAIL_USERNAME'):
        flash('E-mail não configurado. Informe MAIL_USERNAME e MAIL_PASSWORD no arquivo .env para enviar mensagens.', 'danger')
        return redirect(url_for('os.detalhes', id=os.id))

    buffer, nome_arquivo = gerar_pdf_os(os)
    if not buffer:
        flash('Não foi possível gerar o PDF para enviar por e-mail.', 'danger')
        return redirect(url_for('os.detalhes', id=os.id))

    empresa = os.empresa or current_user.empresa
    remetente = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')

    msg = Message(
        subject=f"{os.numero_os} - {'Orçamento' if os.tipo == 'ORCAMENTO' else 'Ordem de Serviço'} | {empresa.nome_fantasia or empresa.razao_social}",
        recipients=[os.cliente.email],
        sender=remetente
    )
    msg.body = _texto_whatsapp(os)
    msg.html = render_template('notificacoes/email_os.html', os=os, empresa=empresa)
    msg.attach(nome_arquivo, 'application/pdf', buffer.read())

    try:
        mail.send(msg)
        flash(f'PDF da {os.numero_os} enviado com sucesso para {os.cliente.email}.', 'success')
    except Exception as e:
        current_app.logger.exception('Falha ao enviar e-mail')
        flash(f'Não foi possível enviar o e-mail: {e}', 'danger')

    return redirect(url_for('os.detalhes', id=os.id))