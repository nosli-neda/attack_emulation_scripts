import os
import json
import time
from datetime import datetime
from scapy.all import sniff, IP, TCP, UDP

# Configurações
LOG_FILE = "/var/log/simoc_traffic.log"
INTERFACE = "eth0"  # Mude para a sua interface de rede atual (ex: ens33, wlan0)
IP_LOCAL = "192.168.29.110"  # O IP da própria máquina de TI

# Dicionário na memória para acumular os bytes por IP de destino
traffic_db = {}

def process_packet(packet):
    if packet.haslayer(IP):
        ip_src = packet[IP].src
        ip_dst = packet[IP].dst
        
        # Queremos apenas pacotes saindo desta máquina para o mundo externo
        if ip_src == IP_LOCAL and ip_dst != "127.0.0.1":
            packet_size = len(packet)
            
            # Acumula o tamanho do pacote para o IP de destino
            if ip_dst not in traffic_db:
                traffic_db[ip_dst] = 0
            traffic_db[ip_dst] += packet_size

def save_logs():
    while True:
        time.sleep(5)  # Atualiza o arquivo de log a cada 5 segundos
        if not traffic_db:
            continue
            
        log_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "host_origem": IP_LOCAL,
            "destinos": []
        }
        
        for ip, bytes_total in traffic_db.items():
            # Converte bytes para MegaBytes para facilitar a leitura no gráfico
            mb_total = round(bytes_total / (1024 * 1024), 2)
            log_data["destinos"].append({
                "ip_destino": ip,
                "megabytes": mb_total
            })
            
        # Grava os dados consolidados no arquivo de log (sobrescrevendo o estado atual)
        try:
            with open(LOG_FILE, "w") as f:
                json.dump(log_data, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar log: {e}")

if __name__ == "__main__":
    print(f"[*] Iniciando monitoramento de tráfego na interface {INTERFACE}...")
    
    # Inicia a thread que salva o log periodicamente
    import threading
    threading.Thread(target=save_logs, daemon=True).start()
    
    # Inicia a captura de pacotes (filtra apenas tráfego TCP e UDP de saída)
    sniff(iface=INTERFACE, prn=process_packet, filter="tcp or udp", store=0)