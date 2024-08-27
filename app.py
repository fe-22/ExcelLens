from flask import Flask, request, render_template, send_file, jsonify
from io import BytesIO
import pandas as pd
import json
import matplotlib.pyplot as plt
import base64

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    # Ler o arquivo Excel ou CSV enviado
    file = request.files['file']
    chart_type = request.form['chart_type']  # Capturar o tipo de gráfico escolhido

    try:
        if file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            df = pd.read_excel(file)
        elif file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            return "Formato de arquivo não suportado. Envie um arquivo Excel ou CSV.", 400

        # Converter colunas de Timestamp para string (ISO 8601)
        df = df.applymap(lambda x: x.isoformat() if isinstance(x, pd.Timestamp) else x)

        # Converter o DataFrame para JSON
        data = df.to_dict(orient='records')
        json_data = json.dumps(data, indent=2)
        
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        return "Erro ao processar o arquivo. Verifique se o arquivo está correto e tente novamente.", 400

    # Exibir o JSON na tela com um botão para plotar gráficos
    return render_template('json_view.html', data=json_data, chart_type=chart_type)

@app.route('/plot_graphs', methods=['POST'])
def plot_graphs():
    # Receber o JSON e convertê-lo em um DataFrame
    json_data = request.form['json_data']
    chart_type = request.form['chart_type']  # Capturar o tipo de gráfico escolhido novamente
    data = json.loads(json_data)
    df = pd.DataFrame(data)

    # Plotar o gráfico de acordo com o tipo selecionado
    plt.figure(figsize=(10, 6))
    if chart_type == 'line':
        df.plot(kind='line')
    elif chart_type == 'bar':
        df.plot(kind='bar')
    elif chart_type == 'scatter':
        df.plot(kind='scatter', x=df.columns[0], y=df.columns[1])  # Ajustar colunas conforme necessário
    elif chart_type == 'hist':
        df.plot(kind='hist')

    # Salvar gráfico em um objeto BytesIO
    output = BytesIO()
    plt.savefig(output, format='png')
    output.seek(0)
    plt.close()

    # Codificar a imagem em Base64
    encoded_img = base64.b64encode(output.getvalue()).decode('utf-8')

    # Retornar o gráfico como uma imagem para exibição
    return render_template('plot_view.html', image=encoded_img, json_data=json_data, chart_type=chart_type)

@app.route('/save_plot', methods=['POST'])
def save_plot():
    # Decodificar a imagem de volta para bytes
    image_data = base64.b64decode(request.form['image'])
    output = BytesIO(image_data)
    output.seek(0)
    return send_file(output, mimetype='image/png', download_name="plot.png", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
