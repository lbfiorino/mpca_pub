# Scripts para geração de _datasets_ de _traces_ de pacotes

Cada arquivos PCAP foi analisado e rotulado individualmente. Posteriormente os arquivos CSVs foram mesclados com o pacote Pandas do Python para formar o _dataset_ completo.

## Arquivos
- **gen_csv_argus_v2.sh/** : _Script_ para gerar _dataset_ com a ferramenta Argus (https://openargus.org/getting-argus) ;
- **gen_csv_cfm_v2.sh /** : _Scripts_ para gerar _dataset_ com a ferramenta CICFLowMeter (https://github.com/lbfiorino/CICFlowMeter);
- **gen_dataset.py/** : _Script_ para mesclar CSVs com Pandas;
