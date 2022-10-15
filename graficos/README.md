# Geração de gráficos


### Arquivos e Pastas

- **pcap_stats** : Pasta contendo as estatisticas (pacotes, bytes) dos tráfegos a partir da análise dos PCAPs a ferramenta `tshark`;  
- **get_pcap_http_req.sh** :  
- **get_pcap_http_srv.sh** :  
- **get_pcap_stats_v3_datetime.sh** : _Script_ para gerar as estatísticas de pacotes e bytes do PCAP. _Considera o tempo relativo entre os pacotes_;  
- **get_pcap_stats_v3_interval_sec.sh** : _Script_ para gerar as estatísticas de pacotes e bytes do PCAP. _Considera a data/hora absoluta em UTC_;  
- **get_pcap_tcp_conversations_stats.sh** : _Script_ para gerar o número de conexões (_tcp conversations_) do PCAP;  
- **get_pcap_tcp_retransmission_stats.sh** : _Script_ para gerar estatísticas de retransmissão do PCAP;  
- **merge_datetime_stats.py** : _Script_ para juntar as estatísticas da ferramenta `tshark` pelo campo _datetime_;  
- **plot_telemetria_original-replay.ipynb** : _Jupyter Notebooks_ para gerar os gráficos de comparação da telemetria;  
- **plot_trafego_original_v3.ipynb** : _Jupyter Notebooks_ para gerar os gráficos de comparação dos PCAPs;  
