# Machine Learning Engineering - Tech Challenge Phase 3

## Clonando o projeto

Para dar os primeiros passos, primeiro devemos clonar o projeto da seguinte maneira:

```bash
git clone git@github.com:r0x0d/mlet_tech_challenge_phase3.git
```

Com o projeto clonado, vamos entrar em sua pasta raíz e instalar as dependencias do projeto

```bash
cd mlet_tech_challenge_phase3
virtualenv vev
./bin/Scripts/activate.ps1
pip install -r requirements.txt
```

```bash
streamlit run mlet_tech_challenge_phase3/__main__.py
```

## Gerando o modelo para utilizar no app

Primeiro, será necessário executar o notebook [Spotify API Dataset](./notebooks/Spotify_API_Dataset.ipynb) para baixar o dataset, tratar e limpar esses dados, e por fim, será possível trabalhar com a parte da modelagem.

Após finalizado a execução do notebook acima, você deverá pegar o dataset limpo que é gerado em formato csv e utilzá-lo no notebook de modelagem, o [Sistema de Recomendação com API do Spotify](./notebooks/Sistema_de_recomendação_com_API_Spotify.ipynb). Ao final da execução de todas as células do notebook, um modelo em formato `.pkl` será gerado. 

Coloque esse modelo na raíz desse repositório e então execute o app streamlit com o seguinte comando:

```bash
streamlit run mlet_tech_challenge_phase3/__main__.py
```
