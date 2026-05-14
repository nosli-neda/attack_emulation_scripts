from scapy.all import IP, TCP, send
import random
import time
import ipaddress

# Alvo da simulação
target_ip = "191.191.58.1"
target_port = 8080

# Blocos de IP reais corrigidos
threat_regions = {
    "Russia": ["95.161.224.0/19", "185.233.184.0/22", "91.215.168.0/22"],
    "China": ["117.136.0.0/16", "220.181.0.0/16", "101.226.0.0/16"],
    "North_Korea": ["175.45.176.0/22"],
    "Iran": ["5.160.0.0/13", "94.232.160.0/20", "185.143.232.0/22"]
}

def get_random_ip(network_cidr):
    net = ipaddress.IPv4Network(network_cidr)
    # Gera um IP aleatório dentro do range da rede (evitando o .0 e o broadcast)
    num_addresses = net.num_addresses
    random_offset = random.randint(1, num_addresses - 2)
    return str(net.network_address + random_offset)

def simular_ataque():
    print(f"[*] SIMOC: Iniciando tráfego real para {target_ip}:{target_port}")
    print("[!] Rodando com Scapy (requer sudo para spoofing)")
    
    try:
        while True:
            # Seleciona uma região e um IP aleatório
            region = random.choice(list(threat_regions.keys()))
            network = random.choice(threat_regions[region])
            spoofed_src = get_random_ip(network)
            
            # Monta o pacote SYN
            packet = IP(src=spoofed_src, dst=target_ip) / \
                     TCP(sport=random.randint(1024, 65535), 
                         dport=int(target_port), 
                         flags="S")
            
            # Envia o pacote para o pfSense
            send(packet, verbose=False)
            print(f"[+] [{region}] Ataque detectado de: {spoofed_src}")
            
            # Ajuste de velocidade (delay entre disparos)
            time.sleep(random.uniform(0.05, 0.15))
            
    except KeyboardInterrupt:
        print("\n[!] Simulação encerrada pelo operador.")

if __name__ == "__main__":
    simular_ataque()