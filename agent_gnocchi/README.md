# Agente de coleta de métricas do serviço de telemetria OpenStack

- **agent-gnocchi-offline_v2.py**: Agente de coleta de métricas a partir da API do Gnocchi;
- **clouds.yml** : Credenciais de acesso a nuvem OpenStack.

### Métricas coletadas do serviço de telemetria da nuvem OpenStack
- **Intervalo entre coletas**: _05 segundos_
```
                cpu_util : Average CPU utilization in %
            memory_usage : Volume of RAM used by the instance from the amount of its allocated memory
          memory_swap_in : Memory swap in
         memory_swap_out : Memory swap out
      disk_read_requests : Number of read requests
     disk_write_requests : Number of write requests
         disk_read_bytes : Volume of reads
        disk_write_bytes : Volume of writes
  network_incoming_bytes : Number of incoming bytes
  network_outgoing_bytes : Number of outgoing bytes
network_incoming_packets : Number of incoming packets
network_outgoing_packets : Number of outgoing packets
```
