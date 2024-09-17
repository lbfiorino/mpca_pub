# _Scripts_ de replicação dos tráfegos http e ataque

Ferramentas de replicação:  
- **GoReplay 1.3.3** (https://goreplay.org/)
  
  Comando para extrair as requisições do PCAP. Parametrizado para gerar apenas um arquivo por PCAP.  
  `gor1.3.3 --verbose 10 --input-raw {PCAP_FILE}:80 --input-raw-engine pcap_file --output-file-size-limit 1TB --output-file-queue-limit 0 --output-file {GOR_FILE}`  

  Commando de replicação dentro do _namespace_.  
  `gor1.3.3 --verbose 1 --stats --input-file {GOR_FILE} --output-http "http://{TARGET_SERVER}"`

- **Tcpreplay 4.4.1** (https://tcpreplay.appneta.com/)

Commando de replicação dentro do _namespace_:  
`tcpreplay --intf1={NS_IFACE} --multiplier=1.000000 {REPLAY_PCAP}`  
Foi observado nos testes que as casas decimais do parâmetro `--multiplier` interfere no desempenho. Foi considerado a mesma precisão da captura, em microssegundos.

## Arquivos e Pastas:  
- **logs** : logs gerados pelos scripts de replicação;
- **createnamespace.py** : Função utilizada pelos _scripts_ de replicação (goreplay, tcpreplay) para criar os namescapes do tipo MACVLAN no Linux;
- **replay_http_goreplay_v2.py** : _Script_ para replicar tráfego http com a ferramenta GoReplay;
- **replay_syn_tcpreplay_v2.py** : _Script_ para replicar tráfego syn-flood com a ferramenta Tcpreplay;
- **extract_synflood_pcap.sh** : _Script_ para extrair os pacotes SYN dos PCAPs para replicação com o _script_ _replay_syn_tcpreplay_v2.py_;
- **goreplay_extract_v2.sh** : _Script_ para extrair as requisições HTTP dos PCAPs para replicação com o _script_ _replay_http_goreplay_v2.py_;

Outros:  
- **add_netns_macvlan_v2.py** : _Script_ para adicionar _namespaces_ do tipo MACVLAN no Linux;
- **edit_http_request_pcap.py** : _Script_ para alterar campos HTTP nos pacotes;
- **edit_mac_ip_pcap.py** : _Script_ para alterar MAC e IP dos pacotes;
- **edit_packet_timestamp.py** : _Script_ para alterar a precisão do _timestamp_ do pacote;
- **replay_syn_moongen_v2.py** : _Script_ para replicar tráfego syn-flood com a ferramenta MoonGen;
