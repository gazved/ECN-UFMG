import matplotlib
matplotlib.use('Agg') 
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
def index():
    filenames = generate_graphs()

    plot_texts = [
        ("plots/boxplot_preco_marca.png", "A ampla variação de preços entre marcas evidencia um mercado competitivo com elementos de diferenciação, típico de um oligopólio diferenciado."),
        ("plots/bar_cpu.png", "A concentração em torno de duas grandes marcas (Intel e AMD) ilustra um duopólio clássico."),
        ("plots/bar_gpu.png", "O mercado de GPUs também é dominado por poucos players (NVIDIA, AMD e Intel), caracterizando um oligopólio concentrado."),
        ("plots/market_presence.png", "A distribuição assimétrica sugere que algumas marcas concentram grande parte da oferta, indicando liderança de mercado."),
        ("plots/avg_price_per_brand.png", "Marcas com preços médios mais altos se posicionam em um segmento premium e exploram poder de marca."),
        ("plots/cpu_price_dist.png", "A comparação direta reforça o duopólio tecnológico entre Intel e AMD."),
        ("plots/gpu_price_dist.png", "A concentração de modelos em poucos tipos de GPU reforça a noção de dependência tecnológica de grandes fabricantes.")
    ]

    return render_template("index.html", plot_texts=plot_texts)
def generate_graphs():
    # Leitura do dataset
    df = pd.read_csv('laptop_cleaned_v2.csv')

    # Conversão de preço para reais
    inr_to_brl = 0.063  # Cotação aproximada
    df['preco_brl'] = df['price'] * inr_to_brl

    # Ajustar o estilo dos gráficos
    sns.set(style="whitegrid")
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12

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

    # 4. Presença de mercado por marca
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

    # 5. Preço médio por marca (em R$)
    fig, ax = plt.subplots(figsize=(12, 6))
    avg_price_brl_by_brand = df.groupby('brand_name')['preco_brl'].mean().sort_values(ascending=False)
    sns.barplot(x=avg_price_brl_by_brand.index, y=avg_price_brl_by_brand.values, palette='magma', ax=ax)
    ax.set_title('Preço Médio dos Laptops por Marca (em R$)')
    ax.set_xlabel('Marca')
    ax.set_ylabel('Preço Médio (R$)')
    plt.xticks(rotation=45)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'avg_price_per_brand.png')
    fig.savefig(filepath)
    filenames.append('plots/avg_price_per_brand.png')
    plt.close(fig)

    # 6. Preço por marca de processador
    fig, ax = plt.subplots(figsize=(10, 6))
    filtered_df = df[df['processor_brand'].isin(['intel', 'amd'])]
    sns.boxplot(data=filtered_df, x='processor_brand', y='preco_brl', palette='Set2', ax=ax)
    ax.set_title('Distribuição de Preços por Marca de Processador (Intel vs AMD)')
    ax.set_xlabel('Marca do Processador')
    ax.set_ylabel('Preço (em R$)')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'cpu_price_dist.png')
    fig.savefig(filepath)
    filenames.append('plots/cpu_price_dist.png')
    plt.close(fig)

    # 7. Preço por tipo de GPU
    fig, ax = plt.subplots(figsize=(12, 6))
    top_gpus = df['graphic_card_name'].value_counts().nlargest(5).index
    filtered_df_gpu = df[df['graphic_card_name'].isin(top_gpus)]
    sns.boxplot(data=filtered_df_gpu, x='graphic_card_name', y='preco_brl', palette='Set3', ax=ax)
    ax.set_title('Distribuição de Preços por Tipo de GPU')
    ax.set_xlabel('Placa de Vídeo')
    ax.set_ylabel('Preço (em R$)')
    plt.xticks(rotation=15)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'gpu_price_dist.png')
    fig.savefig(filepath)
    filenames.append('plots/gpu_price_dist.png')
    plt.close(fig)

    return filenames


@app.route('/static/<path:filename>')
def send_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)







