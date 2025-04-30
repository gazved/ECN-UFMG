from flask import Flask, render_template, send_from_directory
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
from io import BytesIO
import base64

app = Flask(__name__)

# Crie um diretório para armazenar as imagens temporárias
UPLOAD_FOLDER = 'static/plots'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    # Chama a função que gera os gráficos e retorna o nome do arquivo gerado
    graph_filenames = generate_graphs()
    return render_template('index.html', graphs=graph_filenames)

def generate_graphs():
    # Leitura do dataset
    df = pd.read_csv('laptop_cleaned_v2.csv')

    # Ajustar o estilo dos gráficos
    sns.set(style="whitegrid")
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12

    # Gerar gráficos
    filenames = []

    # 1. Distribuição de preços por marca
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=df, x='brand_name', y='price', ax=ax)
    ax.set_title("Distribuição de Preços por Marca")
    ax.set_ylabel("Preço (em R$)")
    ax.set_xlabel("Marca")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'boxplot_preco_marca.png')
    fig.savefig(filepath)
    filenames.append('plots/boxplot_preco_marca.png')
    plt.close(fig)

    # 2. Gráfico de barras para CPUs
    fig, ax = plt.subplots(figsize=(8, 6))
    cpu_counts = df['processor_brand'].value_counts()
    sns.barplot(x=cpu_counts.index, y=cpu_counts.values, ax=ax, palette="pastel")
    ax.set_title("Distribuição das Marcas de CPU")
    ax.set_ylabel("Número de Laptops")
    ax.set_xlabel("Marca de CPU")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'bar_cpu.png')
    fig.savefig(filepath)
    filenames.append('plots/bar_cpu.png')
    plt.close(fig)

    # 3. Gráfico de barras para GPUs
    fig, ax = plt.subplots(figsize=(8, 6))
    df['graphic_card_name_clean'] = df['graphic_card_name'].str.lower().str.extract(r'(nvidia|amd|intel)')
    gpu_counts = df['graphic_card_name_clean'].value_counts()
    sns.barplot(x=gpu_counts.index, y=gpu_counts.values, ax=ax, palette="pastel")
    ax.set_title("Distribuição das Marcas de GPU")
    ax.set_ylabel("Número de Laptops")
    ax.set_xlabel("Marca de GPU")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'bar_gpu.png')
    fig.savefig(filepath)
    filenames.append('plots/bar_gpu.png')
    plt.close(fig)

    # 4. Gráfico de barras de presença de mercado
    fig, ax = plt.subplots(figsize=(12, 6))
    brand_counts = df['brand_name'].value_counts()
    sns.barplot(x=brand_counts.index, y=brand_counts.values, ax=ax, palette='viridis')
    ax.set_title("Presença de Mercado por Marca de Laptop")
    ax.set_xlabel("Marca")
    ax.set_ylabel("Quantidade de Laptops")
    plt.xticks(rotation=45)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'market_presence.png')
    fig.savefig(filepath)
    filenames.append('plots/market_presence.png')
    plt.close(fig)

    return filenames

@app.route('/static/<path:filename>')
def send_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
