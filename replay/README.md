# _Scripts_ de replicação dos tráfegos http e ataque

Ferramentas de replicação:  
- **GoReplay 1.3.3**  
Commando de replicação dentro do namespace:  
`gor1.3.3 --verbose 1 --stats --input-file {GOR_FILE} --output-http "http://{args.target_server}"`
- **Tcpreplay 4.4.1**  
Commando de replicação dentro do namespace:  
`tcpreplay --intf1={ns_iface} --multiplier=1.000000 {replay_pcap}`

## Arquivos e Pastas:  
- **logs** : logs gerados pelos scripts de replicação;
- **createnamespace.py** : Funcão para criar os namescapes de replicação no Linux;
- **replay_http_goreplay_v2.py** : _Script_ para replicar tráfego http com a ferramenta GoReplay;
- **replay_syn_tcpreplay_v2.py** : _Script_ para replicar tráfego syn-flood com a ferramenta Tcpreplay;
- **extract_synflood_pcap.sh** : _Script_ para extrair os pacotes SYN dos PCAPs para replicação com o _script_ _replay_syn_tcpreplay_v2.py_;
- **goreplay_extract_v2.sh** : _Script_ para extrair as requisições HTTP dos PCAPs para replicação com o _script_ _replay_http_goreplay_v2.py_;

Outros:  
- **replay_syn_moongen_v2.py** : _Script_ para replicar tráfego syn-flood com a ferramenta MoonGen;
- **add_netns_macvlan_v2.py** : _Script_ para adicionar _namespaces_ do tipo MACVLAN no Linux;
- **edit_http_request_pcap.py** : _Script_ para alterar campos HTTP nos pacotes;
- **edit_mac_ip_pcap.py** : _Script_ para alterar MAC e IP dos pacotes;
- **edit_packet_timestamp.py** : _Script_ para alterar a precisão do _timestamp_ do pacote;


