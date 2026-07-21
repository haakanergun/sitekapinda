from __future__ import annotations

from dataclasses import dataclass

from .text import normalize_text


@dataclass(frozen=True)
class DemoLayout:
    """Content and composition direction for one generated demo family."""

    family: str
    composition: str
    hero_variant: str
    eyebrow: str
    hero_title: str
    hero_copy: str
    trust_points: tuple[str, str, str]
    section_eyebrow: str
    section_title: str
    section_copy: str
    detail_eyebrow: str
    detail_title: str
    detail_copy: str
    detail_items: tuple[str, str, str]
    cta_title: str
    cta_copy: str
    nav_middle: str


DINING = DemoLayout(
    family="dining",
    composition="menu-story",
    hero_variant="split",
    eyebrow="Mahalle sofrası",
    hero_title="İyi yemek, masada başlayan güzel bir akşam.",
    hero_copy="Menüden rezervasyona uzanan sıcak, sakin ve karar vermeyi kolaylaştıran bir restoran deneyimi.",
    trust_points=("Günün menüsü", "Rezervasyon akışı", "Konum ve saatler"),
    section_eyebrow="Mutfaktan",
    section_title="Masaya gelenler",
    section_copy="İşletmenin gerçek menüsü ve servis biçimi, sahibiyle birlikte netleştirildikten sonra bu alana yerleşir.",
    detail_eyebrow="Sofranın hikâyesi",
    detail_title="Yalnızca yemek değil, geri dönmek isteyeceğiniz bir ritim.",
    detail_copy="Atmosfer, servis ve mutfak yaklaşımı kısa bir anlatıyla buluşur; ziyaretçi rezervasyona geçmeden önce ne bekleyeceğini anlar.",
    detail_items=("Mevsime göre düzenlenebilir seçkiler", "Özel gün ve grup talepleri", "Paket servis ve gel-al bilgisi"),
    cta_title="Masanızı ayırmak için iletişime geçin.",
    cta_copy="Bu önizlemedeki rezervasyon akışı yayın öncesinde işletme sahibinin tercih ettiği kanala bağlanır.",
    nav_middle="Soframız",
)

CAFE = DemoLayout(
    family="cafe-editorial",
    composition="menu-story",
    hero_variant="editorial",
    eyebrow="Günün her saatine",
    hero_title="Mahallenin kısa molası, uzun sohbeti.",
    hero_copy="Menüyü, çalışma saatlerini ve mekânın hissini tek bakışta anlatan rahat bir dijital vitrin.",
    trust_points=("Kahve ve mutfak", "Güncel saatler", "Kolay yol tarifi"),
    section_eyebrow="Tezgahtan",
    section_title="Bugün ne var?",
    section_copy="İçecekler, mutfak seçkisi ve günün duyuruları kolay taranan bir menü düzeninde sunulur.",
    detail_eyebrow="Mekânın ritmi",
    detail_title="İlk kahveden son masaya kadar.",
    detail_copy="Çalışma, buluşma veya kısa bir mola için mekânın sunduğu deneyim net ve samimi bir dille anlatılır.",
    detail_items=("Günün kahvesi ve taze seçkiler", "Masa ve etkinlik bilgisi", "Sosyal kanallara hızlı geçiş"),
    cta_title="Bir masa, bir kahve, iyi bir ara.",
    cta_copy="Menü veya masa bilgisi için işletmenin onayladığı iletişim kanalına geçin.",
    nav_middle="Mekân",
)

BEAUTY = DemoLayout(
    family="beauty-studio",
    composition="editorial-services",
    hero_variant="portrait",
    eyebrow="Kişisel bakım stüdyosu",
    hero_title="Size ayrılan zamanda, özenle.",
    hero_copy="Hizmetleri sakin bir hiyerarşiyle sunan ve randevu kararını kolaylaştıran rafine bir stüdyo sayfası.",
    trust_points=("Randevulu hizmet", "Net bakım seçkisi", "Doğrudan iletişim"),
    section_eyebrow="Bakım seçkisi",
    section_title="İhtiyacınıza göre şekillenen hizmetler",
    section_copy="Uygulama kapsamı, süre ve fiyat yaklaşımı işletme sahibi onayından sonra açık bir dille eklenir.",
    detail_eyebrow="Stüdyo yaklaşımı",
    detail_title="Sakin, kişisel ve iyi planlanmış.",
    detail_copy="İlk görüşmeden son dokunuşa kadar süreç, ziyaretçinin kendini güvende hissedeceği kadar anlaşılır tutulur.",
    detail_items=("Kişiselleştirilebilir bakım planı", "Randevu öncesi kısa bilgilendirme", "Düzenlenebilir hizmet ve fiyat alanları"),
    cta_title="Kendinize uygun zamanı ayırın.",
    cta_copy="Randevu akışı, işletmenin onayladığı telefon veya mesaj kanalına bağlanır.",
    nav_middle="Stüdyo",
)

BARBER = DemoLayout(
    family="barber-workshop",
    composition="editorial-services",
    hero_variant="workshop",
    eyebrow="Usta işi bakım",
    hero_title="Keskin çizgi. Rahat koltuk. Net randevu.",
    hero_copy="Hizmeti, ustalığı ve mahalle bağını güçlü bir ilk izlenimle bir araya getiren berber vitrini.",
    trust_points=("Usta dokunuşu", "Hızlı randevu", "Mahalleye yakın"),
    section_eyebrow="Tezgâhtan",
    section_title="Her detay yerli yerinde",
    section_copy="Kesimden sakal bakımına tüm hizmetler, hızlı karar vermeye uygun net satırlarla sunulur.",
    detail_eyebrow="Ustalık",
    detail_title="Alışkanlık yaratan, tutarlı bir bakım deneyimi.",
    detail_copy="Randevu biçimi, kullanılan hizmet dili ve çalışma saatleri işletmenin gerçek işleyişine göre düzenlenir.",
    detail_items=("Kesim ve şekillendirme", "Sakal ve bakım ritüeli", "Tek dokunuşla telefon veya mesaj"),
    cta_title="Koltuğunuzu ayırtın.",
    cta_copy="Bu demo, işletme sahibinin onayı sonrasında gerçek randevu kanalına yönlendirilir.",
    nav_middle="Ustalık",
)

WORKSHOP = DemoLayout(
    family="technical-workshop",
    composition="service-process",
    hero_variant="technical",
    eyebrow="Servis ve bakım",
    hero_title="Sorunu anlayın. Süreci görün. Güvenle ilerleyin.",
    hero_copy="Paketleri ve teknik hizmetleri anlaşılır bir akışa dönüştüren, hızlı iletişim odaklı servis sayfası.",
    trust_points=("Net servis kapsamı", "Hızlı teklif", "Doğrudan iletişim"),
    section_eyebrow="Servis kapsamı",
    section_title="İhtiyaca göre doğru işlem",
    section_copy="Hizmet kapsamı, işlem adımları ve teklif yöntemi işletmenin gerçek operasyonuna göre netleştirilir.",
    detail_eyebrow="Nasıl ilerler?",
    detail_title="Üç adımda servis talebi",
    detail_copy="Talebinizi iletin, kapsamı birlikte netleştirin ve işletmenin onayladığı zaman planına geçin.",
    detail_items=("Talep ve ön bilgi", "Kapsam ve teklif", "Onaylı servis planı"),
    cta_title="Bakım veya servis talebinizi iletin.",
    cta_copy="Form ve mesaj bağlantıları yayın öncesinde işletmenin gerçek servis akışına göre yapılandırılır.",
    nav_middle="Süreç",
)

HOME_CARE = DemoLayout(
    family="home-care",
    composition="service-process",
    hero_variant="calm",
    eyebrow="Eviniz için planlı hizmet",
    hero_title="Temiz, anlaşılır, zamanında.",
    hero_copy="Bölge, hizmet kapsamı ve teklif adımlarını zahmetsizce anlatan güven odaklı yerel hizmet vitrini.",
    trust_points=("Bölgeye göre hizmet", "Planlı teslim", "Kolay teklif"),
    section_eyebrow="Hizmet planı",
    section_title="Neye ihtiyacınız olduğunu hızla anlatın",
    section_copy="Hizmet türleri ve çalışma bölgeleri işletme sahibinin teyidiyle açık ve kolay taranır biçimde yayınlanır.",
    detail_eyebrow="İşleyiş",
    detail_title="Talep, planlama, teslim",
    detail_copy="Ziyaretçi sürecin nasıl ilerlediğini daha aramadan görür; belirsizlik azalır, doğru talep daha hızlı alınır.",
    detail_items=("İhtiyacın kısa tanımı", "Bölge ve zaman planı", "Onay sonrası hizmet"),
    cta_title="İhtiyacınıza uygun planı konuşalım.",
    cta_copy="Teklif alanı, işletmenin onay verdiği hizmet bölgeleri ve iletişim akışına göre düzenlenir.",
    nav_middle="İşleyiş",
)

BOTANICAL = DemoLayout(
    family="botanical-shop",
    composition="collection",
    hero_variant="botanical",
    eyebrow="Çiçek atölyesi",
    hero_title="Her güne, her hikâyeye taze bir dokunuş.",
    hero_copy="Aranjmanları, teslimat bilgisini ve özel gün siparişlerini görsel bir editoryal akışta buluşturan vitrin.",
    trust_points=("Günlük taze seçki", "Özel gün siparişi", "Teslimat bilgisi"),
    section_eyebrow="Atölyeden",
    section_title="Niyetinize göre bir seçki",
    section_copy="Ürün grupları gerçek fotoğraflar ve işletmenin onayladığı teslimat bilgileriyle kolayca güncellenebilir.",
    detail_eyebrow="Koleksiyonlar",
    detail_title="Kutlamadan içten bir teşekküre",
    detail_copy="Her sipariş niyetine uygun başlangıç noktaları sunulur; ayrıntılar konuşma sırasında kişiselleştirilir.",
    detail_items=("Günlük buketler", "Kutlama ve davetler", "Kişiye özel aranjmanlar"),
    cta_title="Aklınızdaki çiçeği birlikte hazırlayalım.",
    cta_copy="Sipariş bağlantısı, işletmenin teyit ettiği stok ve teslimat yöntemine göre yayına alınır.",
    nav_middle="Koleksiyon",
)

PET_CARE = DemoLayout(
    family="pet-care",
    composition="care-plan",
    hero_variant="friendly",
    eyebrow="Sakin ve dikkatli bakım",
    hero_title="Onların rahatlığı, bakımın ilk adımı.",
    hero_copy="Pet bakım hizmetlerini, hazırlık notlarını ve randevu akışını sahipleri için anlaşılır hale getiren sıcak bir sayfa.",
    trust_points=("Randevulu bakım", "Nazik yaklaşım", "Açık hazırlık notları"),
    section_eyebrow="Bakım menüsü",
    section_title="Her patiye uygun bir rutin",
    section_copy="Hizmet kapsamı ve uygunluk bilgileri, işletmenin yaklaşımına göre açık ve beklenti yönetimi güçlü bir dille düzenlenir.",
    detail_eyebrow="Randevu öncesi",
    detail_title="Daha rahat bir ziyaret için küçük hazırlıklar",
    detail_copy="Petin ihtiyaçları önceden konuşulur, uygun hizmet belirlenir ve randevu zamanı netleştirilir.",
    detail_items=("İhtiyaç ve ırk bilgisi", "Uygun bakım seçimi", "Rahat teslim ve bilgilendirme"),
    cta_title="Bakım randevusunu planlayın.",
    cta_copy="Mesaj ve telefon bağlantıları işletme sahibi onayından sonra gerçek randevu akışına bağlanır.",
    nav_middle="Bakım planı",
)

FITNESS = DemoLayout(
    family="fitness-program",
    composition="schedule",
    hero_variant="kinetic",
    eyebrow="Antrenman ve topluluk",
    hero_title="Bugünkü hareket, yarının ritmi.",
    hero_copy="Üyelik, ders programı ve tanışma randevusunu enerjik ama kolay taranan bir yapıda birleştiren salon vitrini.",
    trust_points=("Ders programı", "Üyelik seçenekleri", "Tanışma randevusu"),
    section_eyebrow="Program",
    section_title="Hedefinize uygun başlangıç",
    section_copy="Dersler, seviye bilgileri ve üyelik seçenekleri işletmenin güncel programına göre düzenlenir.",
    detail_eyebrow="Haftanın ritmi",
    detail_title="Güç, hareket ve toparlanma",
    detail_copy="Program yalnızca ders isimlerini değil, yeni üyelerin nereden başlayabileceğini de açıkça gösterir.",
    detail_items=("Güç ve kondisyon", "Grup dersleri", "Tanışma ve hedef görüşmesi"),
    cta_title="İlk antrenmanınızı planlayın.",
    cta_copy="Tanışma talebi işletmenin onayladığı üyelik danışmanlığı kanalına yönlendirilir.",
    nav_middle="Program",
)

LEARNING = DemoLayout(
    family="learning-path",
    composition="curriculum",
    hero_variant="academic",
    eyebrow="Öğrenme yolculuğu",
    hero_title="Doğru seviye, net plan, güvenli başlangıç.",
    hero_copy="Programları, seviye danışmanlığını ve kayıt talebini öğrenci ile veli için anlaşılır bir yol haritasına dönüştüren kurs sayfası.",
    trust_points=("Program bilgisi", "Seviye görüşmesi", "Kayıt desteği"),
    section_eyebrow="Programlar",
    section_title="Hedefe giden yolu görün",
    section_copy="Ders kapsamı, takvim ve uygun seviye bilgileri kurs yönetiminin onayıyla güncel tutulur.",
    detail_eyebrow="Öğrenme planı",
    detail_title="Tanışmadan düzenli takibe",
    detail_copy="Kayıt öncesi ihtiyaç belirlenir, uygun program seçilir ve ilerleme iletişimi için net bir başlangıç yapılır.",
    detail_items=("Seviye ve hedef görüşmesi", "Uygun program eşleşmesi", "Düzenli ilerleme iletişimi"),
    cta_title="Uygun programı birlikte bulalım.",
    cta_copy="Kayıt talebi, kursun onayladığı danışmanlık ve veli iletişimi akışına bağlanır.",
    nav_middle="Yol haritası",
)

LOCAL_SERVICE = DemoLayout(
    family="local-service",
    composition="service-process",
    hero_variant="calm",
    eyebrow="Yerel hizmet",
    hero_title="İhtiyacınız olan bilgi, tek bir yerde.",
    hero_copy="Hizmetleri, bölge bilgisini ve iletişim adımlarını mobilde kolayca taranan bir vitrinde buluşturur.",
    trust_points=("Mobil uyumlu", "Açık hizmet listesi", "Doğrudan iletişim"),
    section_eyebrow="Hizmetler",
    section_title="Net bir başlangıç noktası",
    section_copy="İçerik, işletme sahibinin gerçek hizmet kapsamı ve çalışma biçimine göre yayın öncesinde düzenlenir.",
    detail_eyebrow="İşleyiş",
    detail_title="Talebinizi kolayca iletin",
    detail_copy="İhtiyaç, kapsam ve iletişim adımları ziyaretçiyi yormadan tek akışta sunulur.",
    detail_items=("İhtiyacı paylaşın", "Kapsamı netleştirin", "Onaylı plana geçin"),
    cta_title="İletişime geçin.",
    cta_copy="Bu önizleme, işletme sahibinin onayıyla gerçek iletişim kanalına bağlanır.",
    nav_middle="İşleyiş",
)


CATEGORY_LAYOUT_FAMILIES: dict[str, DemoLayout] = {
    "restoran": DINING,
    "kafe": CAFE,
    "kuafor": BEAUTY,
    "kuaför": BEAUTY,
    "guzellik salonu": BEAUTY,
    "güzellik salonu": BEAUTY,
    "berber": BARBER,
    "oto yikama": WORKSHOP,
    "oto yıkama": WORKSHOP,
    "oto servis": WORKSHOP,
    "klima servisi": WORKSHOP,
    "hali yikama": HOME_CARE,
    "halı yıkama": HOME_CARE,
    "temizlik firmasi": HOME_CARE,
    "temizlik firması": HOME_CARE,
    "cicekci": BOTANICAL,
    "çiçekçi": BOTANICAL,
    "pet kuaforu": PET_CARE,
    "pet kuaförü": PET_CARE,
    "spor salonu": FITNESS,
    "ozel kurs": LEARNING,
    "özel kurs": LEARNING,
}


def layout_for_category(category: str) -> DemoLayout:
    return CATEGORY_LAYOUT_FAMILIES.get(normalize_text(category), LOCAL_SERVICE)


def family_names() -> set[str]:
    """Return the distinct explicit families, useful for validation and QA."""

    return {layout.family for layout in CATEGORY_LAYOUT_FAMILIES.values()}
