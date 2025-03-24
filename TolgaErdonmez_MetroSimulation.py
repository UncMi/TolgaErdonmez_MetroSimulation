from collections import defaultdict, deque
import heapq
from typing import Dict, List, Set, Tuple, Optional
import matplotlib.pyplot as plt
import networkx as nx
import math

class Istasyon:
    def __init__(self, idx: str, ad: str, hat: str, x=None, y=None):
        self.idx = idx
        self.ad = ad
        self.hat = hat
        self.komsular: List[Tuple['Istasyon', int]] = []  # (istasyon, süre) tuple'ları
        self.x = x
        self.y = y

    def komsu_ekle(self, istasyon: 'Istasyon', sure: int):
        self.komsular.append((istasyon, sure))

class MetroAgi:
    def __init__(self):
        self.istasyonlar: Dict[str, Istasyon] = {}
        self.hatlar: Dict[str, List[Istasyon]] = defaultdict(list)

        # Gösterilecek grafikelr için renklendirme tanımlamaları
        self.hat_renkleri = {
            "Kırmızı Hat": "red",
            "Mavi Hat": "blue",
            "Turuncu Hat": "orange",
        }

    def istasyon_ekle(self, idx: str, ad: str, hat: str, x=None, y=None) -> None:
        if idx not in self.istasyonlar:
            istasyon = Istasyon(idx, ad, hat, x, y)
            self.istasyonlar[idx] = istasyon
            self.hatlar[hat].append(istasyon)

    def baglanti_ekle(self, istasyon1_id: str, istasyon2_id: str, sure: int) -> None:
        istasyon1 = self.istasyonlar[istasyon1_id]
        istasyon2 = self.istasyonlar[istasyon2_id]
        istasyon1.komsu_ekle(istasyon2, sure)
        istasyon2.komsu_ekle(istasyon1, sure)

    def en_az_aktarma_bul(self, baslangic_id: str, hedef_id: str) -> Optional[List[Istasyon]]:
        """BFS algoritması kullanarak en az aktarmalı rotayı bulur"""
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None

        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]

        # BFS için kuyruk oluştur: (istasyon, rota) şeklinde
        kuyruk = deque([(baslangic, [baslangic])])
        ziyaret_edildi = {baslangic}

        while kuyruk:
            istasyon, rota = kuyruk.popleft()

            # Hedef istasyona ulaştıysak, rotayı döndür
            if istasyon.idx == hedef_id:
                return rota

            # Tüm komşuları ziyaret et
            for komsu, _ in istasyon.komsular:
                if komsu not in ziyaret_edildi:
                    # Aktarma durumlarını önceliklendir (aynı hat içinde kalarak)
                    yeni_rota = rota + [komsu]
                    kuyruk.append((komsu, yeni_rota))
                    ziyaret_edildi.add(komsu)

        # Rota bulunamadı
        return None

    def heuristic(self, istasyon: Istasyon, hedef: Istasyon) -> float:
        """A* algoritması için sezgisel fonksiyon (heuristic).Eğer istasyonlar koordinatlara sahipse, Euclidean mesafe hesaplanır.Aksi halde 0 döndürülür."""
        if istasyon.x is not None and istasyon.y is not None and hedef.x is not None and hedef.y is not None:
            return math.sqrt((istasyon.x - hedef.x) ** 2 + (istasyon.y - hedef.y) ** 2)
        return 0

    def en_hizli_rota_bul(self, baslangic_id: str, hedef_id: str) -> Optional[Tuple[List[Istasyon], int]]:
        """A* algoritması kullanarak en hızlı rotayı bulur"""
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None

        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]

        # En iyi süreleri (g değerleri) tutan sözlük
        en_iyi_sureler = {baslangic_id: 0}

        start_h = self.heuristic(baslangic, hedef)
        pq = [(start_h, id(baslangic), baslangic, [baslangic], 0)]
        ziyaret_edildi = set()

        while pq:
            f, _, istasyon, rota, g = heapq.heappop(pq)

            # Hedefe ulaşıldıysa, rotayı ve toplam süreyi döndür
            if istasyon.idx == hedef_id:
                return (rota, g)

            if istasyon.idx in ziyaret_edildi:
                continue

            ziyaret_edildi.add(istasyon.idx)

            for komsu, sure in istasyon.komsular:
                g_new = g + sure

                # Eğer komşu için daha iyi (daha düşük) bir süre bulunmuşsa
                if komsu.idx not in en_iyi_sureler or g_new < en_iyi_sureler[komsu.idx]:
                    en_iyi_sureler[komsu.idx] = g_new
                    h = self.heuristic(komsu, hedef)
                    f_new = g_new + h
                    yeni_rota = rota + [komsu]
                    heapq.heappush(pq, (f_new, id(komsu), komsu, yeni_rota, g_new))

        return None

    def koordinatlari_hesapla(self):
        "Geliştirme amaçla yapılmıştır. Grafikte gösterirken veya gerçek bir aplikasyona uygulanırken bu fonksiyonalite ile beraber scale olması daha kolay olacaktır."
        "İstansyonlar için rastgele (fakat anlamlı) koordinatlar oluşturmaya çalışır."

        hat_pozisyonlari = {}
        for hat_idx, hat in enumerate(self.hatlar.keys()):
            hat_pozisyonlari[hat] = hat_idx

        # Her hat için, istasyonları bir hat boyunca düzenler
        for hat, istasyonlar in self.hatlar.items():
            base_y = hat_pozisyonlari[hat] * 2  # Hatları dikey olarak ayırır
            for i, istasyon in enumerate(sorted(istasyonlar, key=lambda x: x.idx)):
                if istasyon.x is None or istasyon.y is None:  # Koordinatlar zaten ayarlanmamışsa devreye girer
                    istasyon.x = i * 2  # Istasyonları yatay olarak dağıtır
                    istasyon.y = base_y

                    # Aktarma noktaları için, hat ortalamasına yerleştir
                    for komsu, _ in istasyon.komsular:
                        if komsu.hat != istasyon.hat and komsu.x is not None:
                            istasyon.x = (istasyon.x + komsu.x) / 2

        # Aktarma noktalarını hesapla
        for istasyon in self.istasyonlar.values():
            for komsu, _ in istasyon.komsular:
                if komsu.hat != istasyon.hat:
                    komsu.x = istasyon.x

    def metro_agini_goster(self, rota=None, baslik="Metro Ağı"):
        """ Metro ağını ve opsiyonel olarak belirtilen rotayı görselleştirir  """
        G = nx.Graph()


        # Grafik çizmek için kullanılacak düğümleri, kenarları vs. ayarlar
        self.koordinatlari_hesapla()

        for istasyon_id, istasyon in self.istasyonlar.items():
            G.add_node(istasyon_id, pos=(istasyon.x, istasyon.y), label=istasyon.ad, hat=istasyon.hat)

        edge_labels = {}
        for istasyon_id, istasyon in self.istasyonlar.items():
            for komsu, sure in istasyon.komsular:
                # Her bağlantıyı sadece bir kez ekler
                if not G.has_edge(istasyon_id, komsu.idx):
                    # Aktarma bağlantılarını noktalı çizgi ile göster
                    aktarma = istasyon.hat != komsu.hat
                    G.add_edge(istasyon_id, komsu.idx, weight=sure, aktarma=aktarma)
                    edge_labels[(istasyon_id, komsu.idx)] = sure
        pos = nx.get_node_attributes(G, 'pos')

        plt.figure(figsize=(12, 8))
        plt.title(baslik)

        # Düğümleri hat renklerine göre çiz
        hat_gruplari = {}
        for istasyon_id, istasyon in self.istasyonlar.items():
            hat = istasyon.hat
            if hat not in hat_gruplari:
                hat_gruplari[hat] = []
            hat_gruplari[hat].append(istasyon_id)

        # Her hattı ayrı bir renkte çiz
        for hat, istasyonlar in hat_gruplari.items():
            nx.draw_networkx_nodes(G, pos, nodelist=istasyonlar,
                                  node_color=self.hat_renkleri.get(hat, 'gray'),
                                  node_size=500, alpha=0.8)

        # Normal bağlantıları çiz
        normal_edges = [(u, v) for u, v, d in G.edges(data=True) if not d['aktarma']]
        nx.draw_networkx_edges(G, pos, edgelist=normal_edges, width=2)

        # Aktarma bağlantılarını çiz
        aktarma_edges = [(u, v) for u, v, d in G.edges(data=True) if d['aktarma']]
        nx.draw_networkx_edges(G, pos, edgelist=aktarma_edges, width=2,
                               style='dashed', edge_color='purple')

        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

        labels = nx.get_node_attributes(G, 'label')
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)

        # Eğer rota belirtilmişse, rotayı vurgula
        if rota:
            rota_edges = []
            for i in range(len(rota)-1):
                rota_edges.append((rota[i].idx, rota[i+1].idx))

            nx.draw_networkx_edges(G, pos, edgelist=rota_edges,
                                  width=4, edge_color='green', alpha=0.7)

            # Başlangıç ve bitiş istasyonlarını vurgula
            nx.draw_networkx_nodes(G, pos, nodelist=[rota[0].idx],
                                  node_color='green', node_size=700)
            nx.draw_networkx_nodes(G, pos, nodelist=[rota[-1].idx],
                                  node_color='red', node_size=700)

        plt.axis('off')
        plt.tight_layout()
        plt.show()

    def rota_detaylarini_goster(self, rota, toplam_sure=None):
        """ Rotanın detaylarını ve hat geçişlerini gösterir """
        if not rota:
            print("Rota bulunamadı!")
            return

        print("\nRota Detayları:")
        print("-" * 60)
        print(f"Başlangıç: {rota[0].ad} ({rota[0].hat})")

        aktarma_sayisi = 0
        mevcut_hat = rota[0].hat

        for i in range(1, len(rota)):
            onceki = rota[i-1]
            mevcut = rota[i]

            # Hat değişimi varsa, akratma olarak işaretle
            if mevcut.hat != mevcut_hat:
                print(f"AKTARMA: {onceki.ad} istasyonunda {mevcut_hat} -> {mevcut.hat}")
                mevcut_hat = mevcut.hat
                aktarma_sayisi += 1

            # İstasyonlar arası süreyi bul
            sure = 0
            for komsu, s in onceki.komsular:
                if komsu.idx == mevcut.idx:
                    sure = s
                    break

            print(f"{i}. {mevcut.ad} ({mevcut.hat}) - {sure} dakika")

        print("-" * 60)
        print(f"Toplam İstasyon: {len(rota)}")
        print(f"Toplam Aktarma: {aktarma_sayisi}")
        if toplam_sure:
            print(f"Toplam Süre: {toplam_sure} dakika")
        print("-" * 60)

    def en_kalabalik_istasyonlari_bul(self, n=5):
        """ Ağdaki en kalabalık (bağlantı sayısı en çok olan) istasyonları bulur """
        istasyonlar = sorted(self.istasyonlar.values(),
                           key=lambda x: len(x.komsular), reverse=True)
        return istasyonlar[:n]

    def tum_olasi_rotalari_analiz_et(self):
        """ Tüm istasyon çiftleri arasındaki rotaları analiz eder ve ortalama seyahat süresi, aktarma sayısı gibi istatistikler üretir """
        toplam_rota = 0
        toplam_sure = 0
        toplam_aktarma = 0
        max_sure = 0
        max_sure_rota = None

        istasyon_listesi = list(self.istasyonlar.keys())

        for i, baslangic_id in enumerate(istasyon_listesi):
            for hedef_id in istasyon_listesi[i+1:]:
                # En hızlı rotayı bul
                sonuc = self.en_hizli_rota_bul(baslangic_id, hedef_id)
                if sonuc:
                    rota, sure = sonuc
                    toplam_rota += 1
                    toplam_sure += sure

                    # Aktarma sayısını hesapla
                    aktarma_sayisi = 0
                    onceki_hat = None
                    for istasyon in rota:
                        if onceki_hat and istasyon.hat != onceki_hat:
                            aktarma_sayisi += 1
                        onceki_hat = istasyon.hat

                    toplam_aktarma += aktarma_sayisi

                    # En uzun süren rotayı takip et
                    if sure > max_sure:
                        max_sure = sure
                        max_sure_rota = (baslangic_id, hedef_id, rota)

        print("\nAğ Analizi")
        print(f"Toplam İstasyon Çifti: {toplam_rota}")
        if toplam_rota > 0:
            print(f"Ortalama Seyahat Süresi: {toplam_sure/toplam_rota:.2f} dakika")
            print(f"Ortalama Aktarma Sayısı: {toplam_aktarma/toplam_rota:.2f}")
            print(f"En Uzun Rota: {self.istasyonlar[max_sure_rota[0]].ad} -> {self.istasyonlar[max_sure_rota[1]].ad} ({max_sure} dakika)")
            # En uzun rotayı görsel olarak göster
            self.metro_agini_goster(max_sure_rota[2], baslik=f"En Uzun Rota: {max_sure} dakika")

# Örnek Kullanım
if __name__ == "__main__":
    metro = MetroAgi()

    # İstasyonlar ekleme (x, y koordinatlarıyla)
    # Kırmızı Hat
    metro.istasyon_ekle("K1", "Kızılay", "Kırmızı Hat", 5, 3)
    metro.istasyon_ekle("K2", "Ulus", "Kırmızı Hat", 3, 3)
    metro.istasyon_ekle("K3", "Demetevler", "Kırmızı Hat", 1, 3)
    metro.istasyon_ekle("K4", "OSB", "Kırmızı Hat", -1, 3)

    # Mavi Hat
    metro.istasyon_ekle("M1", "AŞTİ", "Mavi Hat", 7, 1)
    metro.istasyon_ekle("M2", "Kızılay", "Mavi Hat", 5, 1)  # Aktarma noktası
    metro.istasyon_ekle("M3", "Sıhhiye", "Mavi Hat", 3, 1)
    metro.istasyon_ekle("M4", "Gar", "Mavi Hat", 1, 1)      # Aktarma noktası

    # Turuncu Hat
    metro.istasyon_ekle("T1", "Batıkent", "Turuncu Hat", -1, 5)
    metro.istasyon_ekle("T2", "Demetevler", "Turuncu Hat", 1, 5)  # Aktarma noktası
    metro.istasyon_ekle("T3", "Gar", "Turuncu Hat", 3, 5)         # Aktarma noktası
    metro.istasyon_ekle("T4", "Keçiören", "Turuncu Hat", 5, 5)

    # Bağlantılar ekleme
    # Kırmızı Hat bağlantıları
    metro.baglanti_ekle("K1", "K2", 4)  # Kızılay -> Ulus
    metro.baglanti_ekle("K2", "K3", 6)  # Ulus -> Demetevler
    metro.baglanti_ekle("K3", "K4", 8)  # Demetevler -> OSB

    # Mavi Hat bağlantıları
    metro.baglanti_ekle("M1", "M2", 5)  # AŞTİ -> Kızılay
    metro.baglanti_ekle("M2", "M3", 3)  # Kızılay -> Sıhhiye
    metro.baglanti_ekle("M3", "M4", 4)  # Sıhhiye -> Gar

    # Turuncu Hat bağlantıları
    metro.baglanti_ekle("T1", "T2", 7)  # Batıkent -> Demetevler
    metro.baglanti_ekle("T2", "T3", 9)  # Demetevler -> Gar
    metro.baglanti_ekle("T3", "T4", 5)  # Gar -> Keçiören

    # Hat aktarma bağlantıları (aynı istasyon farklı hatlar)
    metro.baglanti_ekle("K1", "M2", 2)  # Kızılay aktarma
    metro.baglanti_ekle("K3", "T2", 3)  # Demetevler aktarma
    metro.baglanti_ekle("M4", "T3", 2)  # Gar aktarma


    # Önce tam metro ağını göster
    metro.metro_agini_goster(baslik="Ankara Metro Ağı")

    # Test senaryoları ve görselleştirme
    # Senaryo 1: AŞTİ'den OSB'ye
    print("\nTest Senaryoları")
    print("\n1. AŞTİ'den OSB'ye:")

    # En az aktarmalı rota
    rota = metro.en_az_aktarma_bul("M1", "K4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
        metro.rota_detaylarini_goster(rota)
        metro.metro_agini_goster(rota, baslik="AŞTİ'den OSB'ye (En Az Aktarma)")

    # En hızlı rota
    sonuc = metro.en_hizli_rota_bul("M1", "K4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
        metro.rota_detaylarini_goster(rota, sure)
        metro.metro_agini_goster(rota, baslik=f"AŞTİ'den OSB'ye (En Hızlı): {sure} dakika")

    # Senaryo 2: Batıkent'ten Keçiören'e
    print("\n2. Batıkent'ten Keçiören'e:")

    # En az aktarmalı rota
    rota = metro.en_az_aktarma_bul("T1", "T4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
        metro.rota_detaylarini_goster(rota)
        metro.metro_agini_goster(rota, baslik="Batıkent'ten Keçiören'e (En Az Aktarma)")

    # En hızlı rota
    sonuc = metro.en_hizli_rota_bul("T1", "T4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
        metro.rota_detaylarini_goster(rota, sure)
        metro.metro_agini_goster(rota, baslik=f"Batıkent'ten Keçiören'e (En Hızlı): {sure} dakika")

    # En kalabalık istasyonları göster
    print("\nEn Kalabalık İstasyonlar")
    kalabalik_istasyonlar = metro.en_kalabalik_istasyonlari_bul(3)
    for i, istasyon in enumerate(kalabalik_istasyonlar):
        print(f"{i+1}. {istasyon.ad} ({istasyon.hat}) - {len(istasyon.komsular)} bağlantı")

    # Tüm olası rotaları analiz et
    metro.tum_olasi_rotalari_analiz_et()


    # Senaryo 3: Keçiören'den AŞTİ'ye
    print("\n3. Keçiören'den AŞTİ'ye:")

    # En az aktarmalı rota
    rota = metro.en_az_aktarma_bul("T4", "M1")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
        metro.rota_detaylarini_goster(rota)
        metro.metro_agini_goster(rota, baslik="Keçiören'den AŞTİ'ye (En Az Aktarma)")

    # En hızlı rota
    sonuc = metro.en_hizli_rota_bul("T4", "M1")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
        metro.rota_detaylarini_goster(rota, sure)
        metro.metro_agini_goster(rota, baslik=f"Keçiören'den AŞTİ'ye (En Hızlı): {sure} dakika")

    # Senaryo 4: OSB'den Batıkent'e
    print("\n4. OSB'den Batıkent'e:")

    # Önce daha farklı bir bağlantı ekleyelim ki farklı sonuçlar görebilelim
    # Direk bağlantı olsun ama uzun sürsün
    metro.baglanti_ekle("K4", "T1", 20)  # OSB -> Batıkent direkt ama uzun bağlantı

    # En az aktarmalı rota
    rota = metro.en_az_aktarma_bul("K4", "T1")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
        metro.rota_detaylarini_goster(rota)
        metro.metro_agini_goster(rota, baslik="OSB'den Batıkent'e (En Az Aktarma)")

    # En hızlı rota
    sonuc = metro.en_hizli_rota_bul("K4", "T1")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
        metro.rota_detaylarini_goster(rota, sure)
        metro.metro_agini_goster(rota, baslik=f"OSB'den Batıkent'e (En Hızlı): {sure} dakika")

    # Senaryo 5: Kızılay'dan Keçiören'e, farklı hat bağlantıları üzerinden
    print("\n5. Kızılay'dan Keçiören'e:")

    # Farklı bağlantı seçenekleri ekleyelim
    metro.baglanti_ekle("K1", "T4", 15)  # Kızılay -> Keçiören doğrudan ama uzun bağlantı

    # En az aktarmalı rota
    rota = metro.en_az_aktarma_bul("K1", "T4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
        metro.rota_detaylarini_goster(rota)
        metro.metro_agini_goster(rota, baslik="Kızılay'dan Keçiören'e (En Az Aktarma)")

    # En hızlı rota
    sonuc = metro.en_hizli_rota_bul("K1", "T4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
        metro.rota_detaylarini_goster(rota, sure)
        metro.metro_agini_goster(rota, baslik=f"Kızılay'dan Keçiören'e (En Hızlı): {sure} dakika")

    # Metro ağını son eklemelerle birlikte tekrar göster
    metro.metro_agini_goster(baslik="Güncellenmiş Ankara Metro Ağı")
