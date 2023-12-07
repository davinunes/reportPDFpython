from flask import Flask, request, jsonify
from fpdf import FPDF
from datetime import datetime
import json
import sys
import base64

app = Flask(__name__)


nomes_meses = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        pass

    def bloco_texto_justificado(self, texto, margem_esquerda, margem_direita):
        # Adiciona um bloco de texto justificado com margens
        self.set_left_margin(margem_esquerda)
        self.set_right_margin(margem_direita)
        self.multi_cell(0, 5, texto)
        self.ln()

    def bloco_texto_centralizado(self, texto):
        # Adiciona um bloco de texto centralizado
        self.set_left_margin(0)
        self.set_right_margin(0)
        self.multi_cell(0, 10, texto, align='C')
        self.ln()

    def bloco_texto_direita(self, texto):
        # Adiciona um bloco de texto centralizado
        self.set_left_margin(20)
        self.set_right_margin(20)
        self.multi_cell(0, 10, texto, align='R')
        self.ln()

    def bloco_texto_esquerda(self, texto):
        # Adiciona um bloco de texto centralizado
        self.set_left_margin(20)
        self.set_right_margin(20)
        self.multi_cell(0, 10, texto, align='L')
        self.ln()


@app.route('/gerar_pdf', methods=['POST'])
def gerar_pdf():
    try:
        conteudo_dict = request.get_json()

        if not conteudo_dict:
            raise ValueError("Nenhum JSON foi fornecido.")

        # Criar instância da classe PDF
        pdf = PDF()

        # Adicionar página
        pdf.add_page()

        pdf.image("./LayoutMiami.jpg", x=0, y=0, w=210, h=35)

        # Bloco 1
        pdf.set_xy(0, 35) 
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"PARECER {conteudo_dict['notificacao']}", ln=True, align='C')

        # Bloco 2
        data_atual = datetime.now()
        data_formatada = data_atual.strftime(f"%d de {nomes_meses[data_atual.month - 1]} de %Y")
        pdf.ln(2)
        pdf.set_font("Arial", '', 12)
        pdf.bloco_texto_direita(f"Taguatinga, {data_formatada}")

        # Bloco 3
        texto_bloco3 = f"Unidade: {conteudo_dict['unidade']}\nNotificação: {conteudo_dict['notificacao']}\nAssunto: {conteudo_dict['assunto']}"
        pdf.bloco_texto_justificado(texto_bloco3, 20, 20)

        # Bloco 4
        pdf.ln(2)
        pdf.bloco_texto_justificado("Prezados,\n\nO Conselho Consultivo Fiscal foi convocado para prestar parecer concernente a recurso contra a notificação supracitada referente à infração prevista no Regimento Interno, pautada sobre os artigos acima relacionados.", 20, 20)

        # Bloco 5
        pdf.ln(2)
        pdf.bloco_texto_justificado(f"1. Notificação\nO Condomínio, no uso de suas atribuições administrativas, buscando o cumprimento regimental, notificou a unidade em decorrência de: {conteudo_dict['fato']}", 20, 20)

        # Bloco 6
        pdf.ln(2)
        pdf.bloco_texto_justificado("2. Análise\nForam apreciadas as provas apresentadas pela administração e confrontadas com a argumentação e demais fatos descritos no recurso. ", 20, 20)

        # Bloco 7
        pdf.ln(2)
        pdf.bloco_texto_justificado(f"3. Concluímos\n{conteudo_dict['resultado']}", 20, 20)

        # Bloco 8
        pdf.ln(2)
        pdf.set_font("Arial", 'B', 12)
        pdf.bloco_texto_justificado(f"Somos favoráveis, portanto, em {conteudo_dict['parecer']} a aplicação da penalidade.", 20, 20)


        # Salvar o PDF
        pdf_buffer = pdf.output(dest='S')

        # Verificar o parâmetro na solicitação
        return_as_base64 = request.args.get('base64', '').lower() == 'true'

        if return_as_base64:
            # Converter o PDF para base64
            pdf_base64 = base64.b64encode(pdf_buffer).decode('utf-8')
            return jsonify({'pdf_base64': pdf_base64}), 200
        else:
            # Resposta com o PDF binário
            pdf_bytes = bytearray(pdf_buffer)
            return bytes(pdf_bytes), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'inline; filename=parecer.pdf'}


    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
