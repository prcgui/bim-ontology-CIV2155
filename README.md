# BIM e grafos de conhecimento · CIV2155

**Trabalho aplicado ao projeto arquitetônico FNDE Proinfância Tipo 2, revisão R03.**

O trabalho converte um modelo IFC em RDF e acrescenta associações geométricas entre ambientes, paredes, aberturas e esquadrias. O [Notebook 1](notebooks/01_Arquitetura_IFC_RDF.ipynb) reúne o procedimento executável, as explicações e as referências.

| Para conhecer o trabalho | Onde consultar |
|---|---|
| O que foi feito e como | [Método e alcance](docs/Metodo_e_Alcance.md) |
| Qual código foi usado | [Notebook 1](notebooks/01_Arquitetura_IFC_RDF.ipynb) · [Módulos e consultas](codigo/README.md) |
| O que foi analisado | [Modelo IFC e pranchas R03](dados/README.md) · [Análise dos resultados](docs/Analise_dos_Resultados.md) |
| Quais resultados foram obtidos | [Resultados finais](resultados/README.md) · [Esquadrias por ambiente](resultados/Esquadrias_Por_Ambiente.csv) · [Grafo RDF](resultados/Arquitetura_Analisada.zip) |
| Quais fontes sustentam a implementação | [Referências utilizadas](referencias/README.md) |

**Resultado principal:** dos 41 espaços do IFC, 38 chegaram à associação geométrica e três permaneceram inconclusivos. Foram obtidos **101 pares ambiente–esquadria, envolvendo 66 esquadrias distintas**. Um elemento pode aparecer associado a mais de um ambiente.

Na amostra documental de 14 ambientes, foram recuperados 39 dos 43 casos positivos esperados (**90,7%**). Há uma omissão após a execução e três positivos sem resultado por falha de preparo. Esse percentual descreve a amostra usada no desenvolvimento, sem avaliação independente; não representa a acurácia de todas as associações do edifício.

![Cobertura da execução nos espaços do IFC](resultados/Cobertura.png)

Para executar, abra o notebook no [Google Colab](https://colab.research.google.com/github/prcgui/bim-ontology-CIV2155/blob/main/notebooks/01_Arquitetura_IFC_RDF.ipynb), ou instale as [dependências](requirements.txt) em Python 3.12 e execute as células na ordem. O preparo geométrico é refeito a partir do IFC. A conversão semântica já realizada é reutilizada por padrão; o notebook explica como repeti-la com Java 21.

Este repositório apresenta a rotina selecionada e os seus resultados. O [arquivo técnico no Google Drive](https://drive.google.com/drive/u/0/folders/1kVGXvERWXieeMeURrJF07tuLaADdrJ_O) reúne auditorias, testes, ensaios comparativos e versões anteriores. A reorganização da versão principal preserva o histórico de commits.
