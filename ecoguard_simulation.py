# -*- coding: utf-8 -*-
"""
Necmettin Erbakan Üniversitesi - Bilgisayar Mühendisliği Bölümü
Kablosuz Ağlar Dersi Dönem Ödevi Projesi
Konu: EcoGuard - Dağıtık Akustik Algılama ile Ormanları Koruma Simülasyonu
Öğrenci: Ömer Faruk Kahraman
Öğrenci No: 21370031058
"""

import pygame
import sys
import random
import math

# --- RENKLER (Orman & WSN Konseptli Cyberpunk) ---
COLOR_BG = (10, 20, 15)           # Koyu orman yeşili/siyah arka plan
COLOR_PANEL_BG = (16, 28, 23)     # Panel arka planı
COLOR_TEXT = (220, 245, 230)       # Açık yeşil/beyaz yazı
COLOR_TEXT_MUTED = (120, 150, 135) # Mat yeşil yazı
COLOR_ACCENT = (52, 211, 153)      # Vurgu rengi (Zümrüt Yeşili)

# Harita Nesne Renkleri
COLOR_TREE = (16, 185, 129)        # Ağaçlar (canlı yeşil)
COLOR_TRUNK = (120, 80, 40)        # Ağaç gövdesi (kahverengi)
COLOR_GATEWAY = (99, 102, 241)     # Merkezi İstasyon / Gateway (Mavi/Mor)

# Düğüm (Sensor Node) Renkleri
COLOR_NODE_ACTIVE = (16, 185, 129) # Çalışan sensör düğümü (Yeşil)
COLOR_NODE_ALERT = (239, 68, 68)   # Alarmdaki sensör düğümü (Kırmızı)
COLOR_NODE_SLEEP = (107, 114, 128) # Uyku/Pasif mod düğüm (Gri)
COLOR_LINK = (52, 211, 153, 50)    # Kablosuz bağlantı çizgileri (saydam yeşil)
COLOR_ROUTE = (59, 130, 246)       # Aktif yönlendirme rotası çizgisi (Mavi)

# Dalga ve Paket Renkleri
COLOR_SOUND_WAVE = {
    "CHAINSAW": (249, 115, 22),    # Ağaç Kesim Dalgaları (Turuncu)
    "GUNSHOT": (239, 68, 68),      # Silah Sesi Dalgaları (Kırmızı)
    "VEHICLE": (234, 179, 8)       # Kaçak Araç Dalgaları (Sarı)
}
COLOR_PACKET = (253, 224, 71)      # WSN Veri Paketi (Parlak Sarı)

# --- SİMÜLASYON AYARLARI ---
WIDTH_SIM = 800
HEIGHT_SIM = 800
WIDTH_PANEL = 400
WIDTH_SCREEN = WIDTH_SIM + WIDTH_PANEL
HEIGHT_SCREEN = 800

# --- NESNE SINIFLARI ---

class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(8, 16)
        self.height_offset = random.randint(10, 25) # 2.5D derinlik etkisi için boy farkı
        
    def draw(self, screen):
        # 2.5D Derinlikli ağaç çizimi (gövde + yapraklar)
        pygame.draw.rect(screen, COLOR_TRUNK, (self.x - 2, self.y, 4, self.height_offset))
        pygame.draw.circle(screen, COLOR_TREE, (self.x, self.y - 5), self.size)
        pygame.draw.circle(screen, (5, 150, 95), (self.x - 3, self.y - 8), self.size - 3)

class SoundEvent:
    def __init__(self, x, y, event_type):
        self.x = x
        self.y = y
        self.type = event_type # CHAINSAW, GUNSHOT, VEHICLE
        self.radius = 0.0
        self.max_radius = 280.0 if event_type != "GUNSHOT" else 380.0 # Silah sesi daha uzağa yayılır
        self.speed = 4.0 if event_type == "CHAINSAW" else (7.0 if event_type == "GUNSHOT" else 3.0)
        self.is_active = True
        self.amplitude = 100.0  # Ses şiddeti
        
    def update(self):
        self.radius += self.speed
        # Şiddet mesafe ile azalır (Ters kare yasası)
        self.amplitude = max(0.0, 100.0 * (1.0 - (self.radius / self.max_radius)))
        if self.radius >= self.max_radius:
            self.is_active = False
            
    def draw(self, screen):
        # Genişleyen dairesel ses dalgaları çizer
        alpha = int(255 * (1.0 - (self.radius / self.max_radius)))
        wave_color = COLOR_SOUND_WAVE.get(self.type, (255, 255, 255))
        
        # Saydam halka çizimi
        surface = pygame.Surface((WIDTH_SIM, HEIGHT_SIM), pygame.SRCALPHA)
        pygame.draw.circle(surface, (*wave_color, alpha // 4), (int(self.x), int(self.y)), int(self.radius), 3)
        pygame.draw.circle(surface, (*wave_color, alpha // 8), (int(self.x), int(self.y)), int(self.radius - 15), 1)
        screen.blit(surface, (0, 0))

class SensorNode:
    def __init__(self, node_id, x, y):
        self.id = node_id
        self.x = x
        self.y = y
        
        self.detection_range = 100.0 # Akustik algılama menzili (metre/piksel)
        self.comm_range = 150.0      # Kablosuz haberleşme menzili (metre/piksel)
        self.battery = 100.0         # Pil ömrü (%)
        self.state = "ACTIVE"        # ACTIVE, ALERT, SLEEP, DEAD
        
        self.parent = None           # Ağaç yapısındaki üst düğüm (Routing Parent)
        self.hop_count = 0           # Gateway'e olan hop mesafesi
        self.pulse_time = random.uniform(0, math.pi) # Görsel animasyon için zamanlayıcı

    def update(self):
        # Düğüm uykuda değil veya ölmediyse bataryası çok yavaşça akar (arka plan dinleme)
        if self.state in ["ACTIVE", "ALERT"]:
            self.battery = max(0.0, self.battery - 0.002)
        
        if self.battery <= 0.0:
            self.state = "DEAD"
            
        self.pulse_time += 0.05

    def draw(self, screen, show_ranges):
        # Duruma göre düğüm rengini seç
        if self.state == "DEAD":
            color = (30, 40, 35)
        elif self.state == "ALERT":
            color = COLOR_NODE_ALERT
        elif self.state == "SLEEP":
            color = COLOR_NODE_SLEEP
        else:
            color = COLOR_NODE_ACTIVE
            
        # Görsel darbe (pulsing) etkisi
        pulse_r = 0
        if self.state == "ALERT":
            pulse_r = int(12 + 6 * math.sin(self.pulse_time * 2))
            # Saydam kırmızı alarm halkası çiz
            surf = pygame.Surface((WIDTH_SIM, HEIGHT_SIM), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*COLOR_NODE_ALERT, 50), (int(self.x), int(self.y)), pulse_r)
            screen.blit(surf, (0, 0))
            
        # Ana Düğüm Gövdesi
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 7)
        pygame.draw.circle(screen, COLOR_TEXT, (int(self.x), int(self.y)), 7, 1)
        
        # Düğüm ID Metni
        font = pygame.font.SysFont("Arial", 9)
        id_surf = font.render(str(self.id), True, COLOR_TEXT)
        screen.blit(id_surf, (self.x - 4, self.y - 14))
        
        # Algılama ve Haberleşme Menzili Halkaları (Seçili ise gösterilir)
        if show_ranges and self.state != "DEAD":
            surf = pygame.Surface((WIDTH_SIM, HEIGHT_SIM), pygame.SRCALPHA)
            # Algılama Menzili (Sarı kesik çizgi)
            pygame.draw.circle(surf, (250, 200, 50, 30), (int(self.x), int(self.y)), int(self.detection_range), 1)
            # Haberleşme Menzili (Yeşil/Mavi kesik çizgi)
            pygame.draw.circle(surf, (50, 200, 250, 20), (int(self.x), int(self.y)), int(self.comm_range), 1)
            screen.blit(surf, (0, 0))

class DataPacket:
    def __init__(self, source_node, path, event_type, event_pos):
        self.source = source_node
        self.path = path # Yönlendirme rotası düğüm listesi [node_id_1, node_id_2, ..., Gateway]
        self.event_type = event_type
        self.event_pos = event_pos
        
        self.current_step = 0
        self.x = source_node.x
        self.y = source_node.y
        self.speed = 3.5 # Paket iletim hızı
        self.is_delivered = False
        
    def update(self, nodes, gateway_pos):
        if self.current_step >= len(self.path):
            self.is_delivered = True
            return
            
        # Hedef koordinatı belirle (Rotadaki bir sonraki düğüm veya Gateway)
        next_id = self.path[self.current_step]
        if next_id == -1: # -1 Gateway demektir
            tx, ty = gateway_pos
        else:
            # Rota üzerindeki bir sonraki düğümü bul
            next_node = next(n for n in nodes if n.id == next_id)
            tx, ty = next_node.x, next_node.y
            
        # Hedefe doğru hareket et
        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < self.speed:
            # Hedefe ulaştı, bir sonraki sekmeye (hop) geç
            self.x = tx
            self.y = ty
            
            # Enerji tüketimi (Veri gönderen her düğüm enerji kaybeder)
            if self.current_step < len(self.path):
                sender_id = self.path[self.current_step - 1] if self.current_step > 0 else self.source.id
                if sender_id != -1:
                    sender_node = next((n for n in nodes if n.id == sender_id), None)
                    if sender_node:
                        # Veri paketi iletmek ciddi batarya tüketir
                        sender_node.battery = max(0.0, sender_node.battery - 1.2)
                        
            self.current_step += 1
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            
    def draw(self, screen):
        # Parlak sarı parıldayan paket çizimi
        pygame.draw.circle(screen, COLOR_PACKET, (int(self.x), int(self.y)), 4)
        # Işıma efekti
        surf = pygame.Surface((WIDTH_SIM, HEIGHT_SIM), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*COLOR_PACKET, 100), (int(self.x), int(self.y)), 8)
        screen.blit(surf, (0, 0))

# --- ANA SİMÜLASYON UYGULAMASI ---

class EcoGuardApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("NEÜ Kablosuz Ağlar - EcoGuard DAS Orman Koruma (21370031058)")
        
        self.screen = pygame.display.set_mode((WIDTH_SCREEN, HEIGHT_SCREEN))
        self.clock = pygame.time.Clock()
        self.font_header = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_title = pygame.font.SysFont("Arial", 14, bold=True)
        self.font_body = pygame.font.SysFont("Arial", 13)
        self.font_small = pygame.font.SysFont("Arial", 11)
        
        # Ağ Yapısı Konumlandırması
        self.gateway_x = WIDTH_SIM // 2
        self.gateway_y = HEIGHT_SIM // 2
        self.num_nodes = 24
        
        self.show_ranges = False       # Menzil halkalarını göster/gizle
        self.show_routes = True        # Yönlendirme rotalarını göster/gizle
        self.is_paused = False         # Duraklatma
        
        # İstatistikler
        self.packets_received = 0
        self.alarms_count = 0
        self.active_alarms = []        # Bilgi panelinde gösterilecek aktif alarmlar
        
        self.reset_network()
        
    def reset_network(self):
        """Ağaçları, düğümleri ve kablosuz rotaları sıfırdan oluşturur."""
        self.packets_received = 0
        self.alarms_count = 0
        self.active_alarms = []
        self.sound_events = []
        self.packets = []
        
        # 1. Orman Ağaçlarını Rastgele Oluştur
        self.trees = []
        for _ in range(120):
            tx = random.randint(30, WIDTH_SIM - 30)
            ty = random.randint(30, HEIGHT_SIM - 30)
            # Gateway merkezine ağaç koyma
            if math.dist((tx, ty), (self.gateway_x, self.gateway_y)) > 45:
                self.trees.append(Tree(tx, ty))
                
        # 2. Sensör Düğümlerini Yerleştir (Gateway çevresine halkalar halinde dağıtılır)
        self.nodes = []
        node_id = 1
        
        # 3 farklı halka yarıçapında düğüm yerleşimi yaparak WSN topolojisini kur
        rings = [
            (80.0, 5),   # 1. Halka: 80 piksel yarıçap, 5 düğüm
            (170.0, 8),  # 2. Halka: 170 piksel yarıçap, 8 düğüm
            (260.0, 11)  # 3. Halka: 260 piksel yarıçap, 11 düğüm
        ]
        
        for radius, count in rings:
            for j in range(count):
                angle = (2 * math.pi / count) * j + random.uniform(-0.2, 0.2)
                nx = self.gateway_x + radius * math.cos(angle)
                ny = self.gateway_y + radius * math.sin(angle)
                
                # Sınırlar içinde tut
                nx = max(40, min(WIDTH_SIM - 40, nx))
                ny = max(40, min(HEIGHT_SIM - 40, ny))
                
                self.nodes.append(SensorNode(node_id, nx, ny))
                node_id += 1
                
        # 3. Yönlendirme Ağacını Oluştur (Shortest Path Multi-hop Tree)
        self.rebuild_routes()

    def rebuild_routes(self):
        """
        Düğümler ile Gateway arasındaki en kısa yolları bulur (Ad-hoc Routing).
        Genlik ve haberleşme sınırlarına göre ağaç yapısı kurulur (BFS algoritması ile).
        """
        # Tüm düğüm ebeveynlerini sıfırla
        for node in self.nodes:
            node.parent = None
            node.hop_count = 9999
            
        # Gateway'e doğrudan ulaşabilen düğümleri bul (1-hop komşular)
        queue = []
        for node in self.nodes:
            if node.state == "DEAD":
                continue
            dist_to_gw = math.dist((node.x, node.y), (self.gateway_x, self.gateway_y))
            if dist_to_gw <= node.comm_range:
                node.parent = -1 # -1 Gateway'i temsil eder
                node.hop_count = 1
                queue.append(node)
                
        # Genişlik Öncelikli Arama (BFS) ile diğer düğümlere çok sıçramalı (multi-hop) rota kur
        while queue:
            curr_node = queue.pop(0)
            
            for other in self.nodes:
                if other.state == "DEAD" or other.parent is not None:
                    continue
                    
                # İki düğüm arası kablosuz haberleşme mesafesini test et
                dist_nodes = math.dist((curr_node.x, curr_node.y), (other.x, other.y))
                if dist_nodes <= other.comm_range:
                    other.parent = curr_node.id
                    other.hop_count = curr_node.hop_count + 1
                    queue.append(other)

    def trigger_threat(self, x, y, threat_type):
        """Yeni bir akustik olay (tehdit dalgası) tetikler."""
        # Aynı anda en fazla 5 dalga kontrol et
        if len(self.sound_events) < 5:
            self.sound_events.append(SoundEvent(x, y, threat_type))

    def update_network(self):
        """Tüm ağ elemanlarının, paketlerin ve ses dalgalarının durumunu günceller."""
        # 1. Ses Dalgalarını Güncelle
        for wave in self.sound_events[:]:
            wave.update()
            if not wave.is_active:
                self.sound_events.remove(wave)
                continue
                
            # Dalganın sensör düğümlerine ulaşıp ulaşmadığını kontrol et
            for node in self.nodes:
                if node.state in ["DEAD", "SLEEP"]:
                    continue
                    
                dist = math.dist((wave.x, wave.y), (node.x, node.y))
                # Ses dalgasının ön cephesi sensöre ulaştığında algılama gerçekleşir
                if abs(dist - wave.radius) < wave.speed + 1.0:
                    # Mesafe algılama menzili içindeyse
                    if dist <= node.detection_range:
                        node.state = "ALERT"
                        self.send_alert_packet(node, wave)
                        
        # 2. Sensör Düğümlerini Güncelle
        dead_occurred = False
        for node in self.nodes:
            old_state = node.state
            node.update()
            if node.state == "DEAD" and old_state != "DEAD":
                dead_occurred = True
                
        # Eğer bir düğüm öldüyse ağ rotalarını dinamik olarak yeniden yapılandır (Self-Healing Network)
        if dead_occurred:
            self.rebuild_routes()
            
        # ALERT modundaki düğümleri birkaç saniye sonra tekrar normal aktif moda çek
        # (Gerçek akustik sensörlerin ses durduğunda sakinleşmesi gibi)
        for node in self.nodes:
            if node.state == "ALERT":
                # Etrafta aktif ses dalgası kalmadıysa normale dön
                has_active_wave = False
                for wave in self.sound_events:
                    if math.dist((wave.x, wave.y), (node.x, node.y)) <= node.detection_range:
                        has_active_wave = True
                        break
                if not has_active_wave:
                    node.state = "ACTIVE"
                    
        # 3. Kablosuz Paket İletişimini Güncelle
        for pkt in self.packets[:]:
            pkt.update(self.nodes, (self.gateway_x, self.gateway_y))
            if pkt.is_delivered:
                self.packets.remove(pkt)
                self.packets_received += 1
                self.process_incoming_alarm(pkt)

    def send_alert_packet(self, detection_node, wave):
        """Tespit gerçekleştiren düğümden Gateway'e multi-hop rota üzerinden paket çıkarır."""
        # Düğümün Gateway'e giden rotasını çıkar
        path = []
        curr = detection_node
        visited = set() # Sonsuz döngü engelleme
        
        while curr is not None and curr != -1:
            if curr.id in visited:
                break # Rota döngüye giriyorsa dur
            visited.add(curr.id)
            
            parent_id = curr.parent
            if parent_id == -1:
                path.append(-1) # Son durak Gateway
                break
            elif parent_id is None:
                # Gateway'e giden rota kopuk (İzole Düğüm!)
                break
            else:
                path.append(parent_id)
                curr = next((n for n in self.nodes if n.id == parent_id), None)
                
        # Eğer yol boş değilse paketi oluşturup gönder
        if path:
            # Aynı olay için mükerrer paket gönderimini sınırla (Ağı boğmamak için)
            duplicate = False
            for p in self.packets:
                if p.source.id == detection_node.id and p.event_type == wave.type and math.dist(p.event_pos, (wave.x, wave.y)) < 10:
                    duplicate = True
                    break
            if not duplicate:
                # Düğüm veri paketi üretirken enerji harcar
                detection_node.battery = max(0.0, detection_node.battery - 0.5)
                self.packets.append(DataPacket(detection_node, path, wave.type, (wave.x, wave.y)))

    def process_incoming_alarm(self, packet):
        """Gateway'e ulaşan alarm paketini işler ve sisteme kaydeder."""
        self.alarms_count += 1
        
        # Triangulation/Konum tahmini (Akustik DAS verisi)
        # Paket kaynağı ve olay merkezine hafif gürültü ekleyerek konumu tahmin et
        true_x, true_y = packet.event_pos
        est_error = random.uniform(5.0, 20.0)
        est_x = true_x + random.choice([-1, 1]) * est_error
        est_y = true_y + random.choice([-1, 1]) * est_error
        
        alarm_info = {
            "id": self.alarms_count,
            "type": packet.event_type,
            "source_node": packet.source.id,
            "hops": len(packet.path),
            "pos": (int(est_x), int(est_y)),
            "time": pygame.time.get_ticks()
        }
        
        self.active_alarms.insert(0, alarm_info)
        # Paneli şişirmemek için son 5 alarmı tut
        if len(self.active_alarms) > 5:
            self.active_alarms.pop()

    def draw_simulation(self):
        """Sol taraftaki orman haritasını ve kablosuz ağı çizer."""
        # Orman zeminini çiz (koyu yeşil)
        self.screen.fill(COLOR_BG)
        
        # Kablosuz Haberleşme Linklerini Çiz (Mesh Yapısı)
        for node in self.nodes:
            if node.state == "DEAD":
                continue
            # Düğüm üst ebeveynine bağlıysa bağlantı çizgisini çiz
            if node.parent is not None:
                if node.parent == -1:
                    px, py = self.gateway_x, self.gateway_y
                else:
                    parent_node = next((n for n in self.nodes if n.id == node.parent), None)
                    px, py = (parent_node.x, parent_node.y) if parent_node else (node.x, node.y)
                
                # Rota çizgisi rengi
                line_color = COLOR_ROUTE if self.show_routes else (40, 70, 55)
                pygame.draw.line(self.screen, line_color, (node.x, node.y), (px, py), 1)
                
        # Ses Dalgası Halkalarını Çiz
        for wave in self.sound_events:
            wave.draw(self.screen)
            
        # Ağaçları Çiz
        for tree in self.trees:
            tree.draw(self.screen)
            
        # Merkezi İstasyon / Gateway İstasyonunu Çiz
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, (self.gateway_x - 18, self.gateway_y - 18, 36, 36), 0, 4)
        pygame.draw.rect(self.screen, COLOR_GATEWAY, (self.gateway_x - 18, self.gateway_y - 18, 36, 36), 2, 4)
        # Anten sembolü
        pygame.draw.line(self.screen, COLOR_GATEWAY, (self.gateway_x, self.gateway_y - 10), (self.gateway_x, self.gateway_y + 10), 2)
        pygame.draw.circle(self.screen, COLOR_GATEWAY, (self.gateway_x, self.gateway_y - 10), 4)
        
        # Sensör Düğümlerini Çiz
        for node in self.nodes:
            node.draw(self.screen, self.show_ranges)
            
        # Veri Paketlerini Çiz
        for pkt in self.packets:
            pkt.draw(self.screen)
            
        # Alarm Verilen Tahmini Konum İşaretlerini Çiz
        current_time = pygame.time.get_ticks()
        for alarm in self.active_alarms:
            # Alarm oluştuktan sonra 4 saniye boyunca haritada yanıp söner
            if current_time - alarm["time"] < 4000:
                ax, ay = alarm["pos"]
                # Yanıp sönen halka
                pulse = int(10 + 10 * math.sin(current_time * 0.01))
                color = COLOR_SOUND_WAVE.get(alarm["type"], (255, 255, 255))
                pygame.draw.circle(self.screen, color, (ax, ay), pulse, 1)
                # Merkez artı işareti
                pygame.draw.line(self.screen, color, (ax - 8, ay), (ax + 8, ay), 2)
                pygame.draw.line(self.screen, color, (ax, ay - 8), (ax, ay + 8), 2)
                
                # Alarm Etiketi
                lbl = self.font_small.render(f"ALARM #{alarm['id']}", True, color)
                self.screen.blit(lbl, (ax + 10, ay - 10))

    def draw_panel(self):
        """Sağ taraftaki gösterge tablosunu çizer."""
        panel_rect = (WIDTH_SIM, 0, WIDTH_PANEL, HEIGHT_SCREEN)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, panel_rect)
        pygame.draw.line(self.screen, COLOR_ACCENT, (WIDTH_SIM, 0), (WIDTH_SIM, HEIGHT_SCREEN), 2)
        
        y_offset = 25
        
        # 1. Başlıklar
        header_text = self.font_header.render("NECMETTİN ERBAKAN ÜNİ.", True, COLOR_TEXT)
        self.screen.blit(header_text, (WIDTH_SIM + 25, y_offset))
        y_offset += 22
        
        sub_header = self.font_title.render("Kablosuz Ağlar Dersi Dönem Projesi", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub_header, (WIDTH_SIM + 25, y_offset))
        y_offset += 30
        
        title_eco = self.font_title.render("EcoGuard: Dağıtık Akustik Algılama", True, COLOR_ACCENT)
        self.screen.blit(title_eco, (WIDTH_SIM + 25, y_offset))
        y_offset += 20
        
        std_text = self.font_body.render("Ömer Faruk Kahraman - 21370031058", True, COLOR_TEXT)
        self.screen.blit(std_text, (WIDTH_SIM + 25, y_offset))
        
        # Ayırıcı Hat
        y_offset += 30
        pygame.draw.line(self.screen, (25, 45, 35), (WIDTH_SIM + 20, y_offset), (WIDTH_SCREEN - 20, y_offset), 1)
        y_offset += 20
        
        # 2. Ağ İstatistikleri
        stat_title = self.font_title.render("KABLOSUZ SENSÖR AĞI (WSN) ANALİZİ", True, COLOR_ACCENT)
        self.screen.blit(stat_title, (WIDTH_SIM + 25, y_offset))
        y_offset += 30
        
        # Aktif / Ölü Düğüm Sayısı
        active_cnt = sum(1 for n in self.nodes if n.state != "DEAD")
        dead_cnt = len(self.nodes) - active_cnt
        node_stats = self.font_body.render(f"Aktif Düğüm: {active_cnt}  |  Ölü Düğüm: {dead_cnt}  (Toplam: {len(self.nodes)})", True, COLOR_TEXT)
        self.screen.blit(node_stats, (WIDTH_SIM + 25, y_offset))
        y_offset += 25
        
        # İletilen Toplam Paket
        pkt_stats = self.font_body.render(f"Merkeze Ulaşan Paket Sayısı: {self.packets_received}", True, COLOR_TEXT)
        self.screen.blit(pkt_stats, (WIDTH_SIM + 25, y_offset))
        y_offset += 25
        
        # Ortalama Rota Derinliği (Hop Count)
        connected_nodes = [n for n in self.nodes if n.hop_count < 9999]
        avg_hops = sum(n.hop_count for n in connected_nodes) / len(connected_nodes) if connected_nodes else 0.0
        hop_stats = self.font_body.render(f"Ortalama Sıçrama (Hop) Sayısı: {avg_hops:.1f} hop", True, COLOR_TEXT)
        self.screen.blit(hop_stats, (WIDTH_SIM + 25, y_offset))
        y_offset += 25
        
        # Ağ Sağlık Durumu (Bağlantı yüzdesi)
        health_pct = (len(connected_nodes) / len(self.nodes)) * 100.0 if self.nodes else 0.0
        health_color = COLOR_TREE if health_pct > 80 else ((234, 179, 8) if health_pct > 50 else COLOR_NODE_ALERT)
        health_text = self.font_body.render(f"Şebeke Bağlantı Sağlığı: %{health_pct:.1f}", True, health_color)
        self.screen.blit(health_text, (WIDTH_SIM + 25, y_offset))
        
        # Ayırıcı Hat
        y_offset += 35
        pygame.draw.line(self.screen, (25, 45, 35), (WIDTH_SIM + 20, y_offset), (WIDTH_SCREEN - 20, y_offset), 1)
        y_offset += 20
        
        # 3. Son Alınan Tehdit Uyarıları
        alarm_title = self.font_title.render("MERKEZİ ALARM GÜNLÜĞÜ (SON 3)", True, COLOR_ACCENT)
        self.screen.blit(alarm_title, (WIDTH_SIM + 25, y_offset))
        y_offset += 30
        
        if not self.active_alarms:
            no_alarm = self.font_body.render("Tehlike tespit edilmedi. Sistem güvenli.", True, COLOR_TEXT_MUTED)
            self.screen.blit(no_alarm, (WIDTH_SIM + 25, y_offset))
            y_offset += 30
        else:
            for alarm in self.active_alarms[:3]:
                color = COLOR_SOUND_WAVE.get(alarm["type"], COLOR_TEXT)
                txt_alarm = f"ALARM #{alarm['id']} - {alarm['type']}"
                surf_al = self.font_title.render(txt_alarm, True, color)
                self.screen.blit(surf_al, (WIDTH_SIM + 25, y_offset))
                y_offset += 18
                
                txt_det = f"Konum: ({alarm['pos'][0]}, {alarm['pos'][1]}) | Sekme: {alarm['hops']} Hop | Kaynak Düğüm: ID {alarm['source_node']}"
                surf_det = self.font_small.render(txt_det, True, COLOR_TEXT_MUTED)
                self.screen.blit(surf_det, (WIDTH_SIM + 25, y_offset))
                y_offset += 22
                
        # Ayırıcı Hat
        y_offset += 15
        pygame.draw.line(self.screen, (25, 45, 35), (WIDTH_SIM + 20, y_offset), (WIDTH_SCREEN - 20, y_offset), 1)
        y_offset += 20
        
        # 4. İnteraktif Tehdit Kontrol Paneli
        ctrl_title = self.font_title.render("İNTERAKTİF TEHDİT KONTROLLERİ", True, COLOR_ACCENT)
        self.screen.blit(ctrl_title, (WIDTH_SIM + 25, y_offset))
        y_offset += 30
        
        controls = [
            ("Sol Tık", "Ağaç Kesimi Sesi (Chainsaw) Tetikler"),
            ("Sağ Tık", "Avcı Silah Sesi (Gunshot) Tetikler"),
            ("Orta Tık / C", "Kaçak Araç Sesi (Vehicle) Tetikler"),
            ("R Tuşu", "Tüm Ağı Yeniden Yapılandırır (Reset)"),
            ("H Tuşu", "WSN Kablosuz Bağlantıları Göster/Gizle"),
            ("V Tuşu", "Düğümlerin Tarama Menzillerini Göster"),
            ("Space", "Simülasyonu Duraklat / Devam Et")
        ]
        
        for key, desc in controls:
            key_surf = self.font_title.render(key, True, COLOR_TEXT)
            self.screen.blit(key_surf, (WIDTH_SIM + 25, y_offset))
            desc_surf = self.font_body.render(desc, True, COLOR_TEXT_MUTED)
            self.screen.blit(desc_surf, (WIDTH_SIM + 130, y_offset))
            y_offset += 22
            
        if self.is_paused:
            y_offset += 15
            paused_surf = self.font_header.render("SİMÜLASYON DURAKLATILDI", True, COLOR_NODE_ALERT)
            self.screen.blit(paused_surf, (WIDTH_SIM + 60, y_offset))

    def run(self):
        """Simülasyon döngüsünü başlatır."""
        running = True
        while running:
            self.clock.tick(60)
            
            # --- OLAY KONTROLLERİ ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Tıklanan konum simülasyon sınırları içindeyse akustik tehdit oluştur
                    mx, my = event.pos
                    if 0 <= mx < WIDTH_SIM and 0 <= my < HEIGHT_SIM:
                        if event.button == 1:   # Sol tık -> Motorlu Testere
                            self.trigger_threat(mx, my, "CHAINSAW")
                        elif event.button == 3: # Sağ tık -> Silah Sesi
                            self.trigger_threat(mx, my, "GUNSHOT")
                        elif event.button == 2: # Orta tık -> Kaçak Araç
                            self.trigger_threat(mx, my, "VEHICLE")
                            
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.is_paused = not self.is_paused
                    elif event.key == pygame.K_r:
                        self.reset_network()
                    elif event.key == pygame.K_h:
                        self.show_routes = not self.show_routes
                    elif event.key == pygame.K_v:
                        self.show_ranges = not self.show_ranges
                    elif event.key == pygame.K_c:
                        # Klavye kısayolu ile araç tehdidi
                        mx, my = pygame.mouse.get_pos()
                        if 0 <= mx < WIDTH_SIM and 0 <= my < HEIGHT_SIM:
                            self.trigger_threat(mx, my, "VEHICLE")
                            
            # --- FİZİK VE DÜĞÜM DÖNGÜSÜ ---
            if not self.is_paused:
                self.update_network()
                
            # --- ÇİZİM DÖNGÜSÜ ---
            self.draw_simulation()
            self.draw_panel()
            
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = EcoGuardApp()
    app.run()
