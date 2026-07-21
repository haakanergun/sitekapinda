from __future__ import annotations

import hashlib
import html
import json
import shutil
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

from .compliance import validate_generated_html
from .demo_layouts import DemoLayout, layout_for_category
from .models import GeneratedPage, ScoredCandidate
from .text import ascii_slug, normalize_phone, normalize_text


@dataclass(frozen=True)
class CategoryProfile:
    intro: str
    services: tuple[str, ...]
    proof_points: tuple[str, ...]
    palette: tuple[str, str, str, str]
    type_scale: str
    tone: str
    visual_direction: str
    cta_primary: str
    cta_secondary: str
    icon: str


DEFAULT_PROFILE = CategoryProfile(
    intro="Yerel işletme bilgilerini hızlı, mobil uyumlu ve kolay düzenlenebilir bir web sitesi önizlemesinde toplar.",
    services=("Hizmet listesi", "Konum bilgisi", "Hızlı iletişim", "Teklif veya randevu talebi"),
    proof_points=("Mobil uyumlu önizleme", "Yerel SEO'ya hazır teknik altyapı", "İşletme onayıyla düzenlenebilir içerik"),
    palette=("#17201b", "#f7f0e4", "#0f766e", "#e1c16e"),
    type_scale="Net, okunaklı, modern sans-serif",
    tone="sade, güven veren ve doğrudan",
    visual_direction="yerel hizmet vitrini, temiz yüzeyler, net aksiyonlar",
    cta_primary="Teklif talebi",
    cta_secondary="Ara",
    icon="spark",
)

TURKISH_UI_TEXT_RULE = (
    "If a generated visual contains Turkish UI text, every visible Turkish word must use correct Turkish characters "
    "and natural Turkish spelling. Use examples such as aracınıza, iletişim, işletme, hızlı, görün, bakım, "
    "randevu talebi, hizmetler. Never transliterate Turkish into ASCII-only forms such as araciniza, iletisim, "
    "isletme, hizli, gorun, bakim. If Turkish text cannot be rendered reliably, use fewer words or no text instead "
    "of incorrect Turkish."
)


CATEGORY_PROFILES: dict[str, CategoryProfile] = {
    "kuafor": CategoryProfile(
        intro="Saç kesimi, renklendirme ve günlük bakım ihtiyaçlarını tek bakışta anlatan rafine bir randevu sayfası.",
        services=("Saç kesimi", "Fön ve bakım", "Renklendirme danışmanlığı", "Randevu yönetimi"),
        proof_points=("Hizmetler net ayrışır", "Telefon ve WhatsApp öne çıkar", "Görsel ton salon atmosferine göre değiştirilebilir"),
        palette=("#231a22", "#fff4f7", "#b83b5e", "#f1b6c8"),
        type_scale="Yumuşak başlıklar, kısa servis satırları",
        tone="bakımlı, sakin ve davetkar",
        visual_direction="ayna yansımaları, sıcak salon ışığı, zarif bakım dokuları",
        cta_primary="Randevu iste",
        cta_secondary="Ara",
        icon="scissors",
    ),
    "berber": CategoryProfile(
        intro="Mahalle berberi için hizmet, saat ve hızlı iletişim odağını güçlü bir ilk ekrana taşıyan demo.",
        services=("Saç kesimi", "Sakal düzenleme", "Bakım paketleri", "Hızlı randevu"),
        proof_points=("Tek dokunuşla arama", "Mahalle odaklı konum anlatımı", "Kolay güncellenen hizmet listesi"),
        palette=("#171717", "#f5efe6", "#9b1c31", "#c8a45d"),
        type_scale="Güçlü başlıklar, keskin servis listeleri",
        tone="usta işi, net ve güvenli",
        visual_direction="barber pole ritmi, koyu yüzeyler, metalik bakım araçları",
        cta_primary="Randevu iste",
        cta_secondary="WhatsApp",
        icon="razor",
    ),
    "guzellik salonu": CategoryProfile(
        intro="Bakım ve güzellik hizmetlerini sakin, anlaşılır ve güven veren bir randevu akışında toplar.",
        services=("Cilt bakım bilgilendirmesi", "Kaş ve kirpik hizmetleri", "Bakım paketleri", "Randevu talebi"),
        proof_points=("Hizmetleri düzenli gösterir", "Randevu akışını kolaylaştırır", "Onay sonrası marka tonuna uyarlanır"),
        palette=("#2b1f2f", "#fff7f0", "#8f4f7f", "#e8b7a7"),
        type_scale="Zarif başlıklar, ferah açıklamalar",
        tone="özenli, sıcak ve temiz",
        visual_direction="yumuşak doku, bakım tezgahı, açık tonlu premium yüzeyler",
        cta_primary="Randevu talebi",
        cta_secondary="Ara",
        icon="spark",
    ),
    "oto yikama": CategoryProfile(
        intro="Araç yıkama ve bakım paketlerini hızlıca karşılaştırmaya uygun, enerjik bir teklif sayfası.",
        services=("Dış yıkama", "İç temizlik", "Detaylı bakım", "Paket teklifi"),
        proof_points=("Paketler hızlı taranır", "Telefon ve konum görünür olur", "Hızlı yüklenen yalın yapı"),
        palette=("#071923", "#eef9ff", "#0984a8", "#8ee3f5"),
        type_scale="Keskin, teknik ve hızlı okunur",
        tone="temiz, hızlı ve pratik",
        visual_direction="su çizgileri, parlak kaporta, mavi servis ışığı",
        cta_primary="Paket teklifi al",
        cta_secondary="Ara",
        icon="car",
    ),
    "oto servis": CategoryProfile(
        intro="Servis, bakım ve arıza taleplerini düzenli gösteren güvenli ve teknik bir önizleme taslağı.",
        services=("Periyodik bakım", "Arıza tespiti", "Yağ ve filtre değişimi", "Teklif talebi"),
        proof_points=("Servis kapsamı netleşir", "Teklif formu için hazır alan sunar", "Usta onayıyla kolayca düzenlenir"),
        palette=("#1b1d20", "#f4f1e9", "#b64b27", "#e1a95f"),
        type_scale="Teknik başlıklar, net açıklamalar",
        tone="sağlam, pratik ve güven veren",
        visual_direction="servis çizgileri, metal dokular, sıcak atölye ışığı",
        cta_primary="Servis talebi",
        cta_secondary="Ara",
        icon="wrench",
    ),
    "hali yikama": CategoryProfile(
        intro="Halı yıkama taleplerini, bölge bilgisini ve teslim akışını hızlıca anlatan yerel hizmet demosu.",
        services=("Halı yıkama", "Koltuk yıkama", "Yerinden teslim alma", "Teklif talebi"),
        proof_points=("Bölge odaklı anlatım", "Hızlı teklif alanı", "Mobil ziyaretçiler için net CTA"),
        palette=("#24352f", "#f7f3ea", "#2f7d64", "#d6a85f"),
        type_scale="Yumuşak, temiz ve ev hizmeti odaklı",
        tone="temiz, erişilebilir ve güvenli",
        visual_direction="dokuma çizgileri, ferah ev ışığı, temiz tekstil hissi",
        cta_primary="Teklif iste",
        cta_secondary="Ara",
        icon="home",
    ),
    "klima servisi": CategoryProfile(
        intro="Klima bakım ve servis talepleri için arama, WhatsApp ve form akışını birleştiren teknik önizleme.",
        services=("Klima bakımı", "Arıza tespiti", "Montaj talebi", "Periyodik servis"),
        proof_points=("Acil iletişim görünür olur", "Hizmet kapsamı sadeleşir", "Sezona göre güncellenebilir"),
        palette=("#102331", "#eff8fb", "#0e80a5", "#7ed3e8"),
        type_scale="Serin, teknik ve okunaklı",
        tone="hızlı, net ve servis odaklı",
        visual_direction="serin hava akışı, teknik çizgiler, açık mavi ışık",
        cta_primary="Servis talebi",
        cta_secondary="WhatsApp",
        icon="snow",
    ),
    "cicekci": CategoryProfile(
        intro="Çiçek siparişi ve özel gün taleplerini zarif, hızlı ve kolay düzenlenebilir bir vitrine taşır.",
        services=("Buklet hazırlığı", "Özel gün aranjmanı", "Teslimat bilgisi", "Sipariş talebi"),
        proof_points=("Sipariş aksiyonu öne çıkar", "Ürün grupları net görünür", "Görsel alanlar sonradan eklenebilir"),
        palette=("#203125", "#fff7ec", "#2e8b57", "#f0b85a"),
        type_scale="Doğal başlıklar, kısa sipariş adımları",
        tone="zarif, taze ve samimi",
        visual_direction="çiçek yaprakları, gün ışığı, doğal renk geçişleri",
        cta_primary="Sipariş talebi",
        cta_secondary="Ara",
        icon="flower",
    ),
    "pet kuaforu": CategoryProfile(
        intro="Pet bakım randevularını ve hizmet kapsamını anlaşılır şekilde sunan sıcak bir önizleme.",
        services=("Tüy bakımı", "Banyo ve kurutma", "Tırnak bakımı", "Randevu talebi"),
        proof_points=("Randevu akışı basitleşir", "Hizmetler sakin dille anlatılır", "İşletme tonuna göre düzenlenebilir"),
        palette=("#1e2a2f", "#fff4e8", "#2f8f83", "#f0a55c"),
        type_scale="Samimi ama düzenli servis dili",
        tone="sıcak, dikkatli ve güven veren",
        visual_direction="yumuşak bakım dokuları, dostane stüdyo ışığı, temiz masaüstü",
        cta_primary="Randevu talebi",
        cta_secondary="WhatsApp",
        icon="paw",
    ),
    "kafe": CategoryProfile(
        intro="Menü, konum ve iletişim bilgilerini rahatça taranabilir hale getiren modern kafe önizlemesi.",
        services=("Kahve ve içecekler", "Atıştırmalıklar", "Masa bilgisi", "Etkinlik duyuruları"),
        proof_points=("Menüye hızlı erişim sağlar", "Konumu görünür yapar", "Günün ritmine göre güncellenebilir"),
        palette=("#241c18", "#fff6e9", "#5b8a72", "#d8a05f"),
        type_scale="Sıcak başlıklar, menü gibi taranan satırlar",
        tone="rahat, yerel ve davetkar",
        visual_direction="tezgah ışığı, kahve dokusu, samimi mahalle ritmi",
        cta_primary="Menüyü sor",
        cta_secondary="Ara",
        icon="cup",
    ),
    "restoran": CategoryProfile(
        intro="Restoranın menü, rezervasyon ve konum bilgisini toparlayan sade bir demo web sayfası.",
        services=("Menü alanı", "Rezervasyon talebi", "Paket servis bilgisi", "Konum yönlendirmesi"),
        proof_points=("Rezervasyon aksiyonu netleşir", "Mobil ziyaretçiye uygundur", "Menü sonradan kolayca düzenlenir"),
        palette=("#2b1712", "#fff8ee", "#9e4f2f", "#e0b15f"),
        type_scale="Sofra sıcaklığı taşıyan okunaklı başlıklar",
        tone="iştah açıcı, düzenli ve sıcak",
        visual_direction="masa yüzeyi, sıcak servis ışığı, sade tabak detayları",
        cta_primary="Rezervasyon iste",
        cta_secondary="Ara",
        icon="plate",
    ),
    "spor salonu": CategoryProfile(
        intro="Üyelik, dersler ve iletişim akışını düzenli gösteren mobil uyumlu bir spor salonu demo sayfası.",
        services=("Üyelik bilgisi", "Grup dersleri", "Antrenman danışmanlığı", "Tanışma randevusu"),
        proof_points=("Programlar düzenli sunulur", "Yeni üye talebi kolaylaşır", "Kampanya alanları eklenebilir"),
        palette=("#111827", "#f2f5f7", "#ef4444", "#facc15"),
        type_scale="Enerjik başlıklar, kısa aksiyon satırları",
        tone="dinamik, temiz ve hedef odaklı",
        visual_direction="hareket çizgileri, güçlü kontrast, spor alanı enerjisi",
        cta_primary="Tanışma randevusu",
        cta_secondary="Ara",
        icon="bolt",
    ),
    "ozel kurs": CategoryProfile(
        intro="Kurs programları, kayıt talebi ve konum bilgisini anlaşılır hale getiren eğitim odaklı demo.",
        services=("Program bilgisi", "Seviye danışmanlığı", "Kayıt talebi", "Veli iletişimi"),
        proof_points=("Kayıt süreci sadeleşir", "Programlar net gösterilir", "İçerik işletme onayıyla düzenlenir"),
        palette=("#172554", "#f4f7ff", "#2563eb", "#f2c94c"),
        type_scale="Akademik ama sıcak, düzenli bilgi hiyerarşisi",
        tone="açık, yönlendirici ve güvenli",
        visual_direction="defter çizgileri, açık masa, öğrenme ritmi",
        cta_primary="Kayıt bilgisi al",
        cta_secondary="Ara",
        icon="book",
    ),
    "temizlik firmasi": CategoryProfile(
        intro="Ev ve iş yeri temizlik talepleri için teklif almaya uygun, net ve hızlı bir sayfa önizlemesi.",
        services=("Ev temizliği", "Ofis temizliği", "Periyodik hizmet", "Teklif talebi"),
        proof_points=("Teklif akışı kolaylaşır", "Bölge ve hizmetler netleşir", "Satış ekibinin gösterebileceği hazır demo"),
        palette=("#12312f", "#effaf6", "#14a085", "#9be7d0"),
        type_scale="Ferah, hijyenik ve açık bilgi dili",
        tone="temiz, düzenli ve güven veren",
        visual_direction="parlak yüzey, ferah ışık, düzenli hizmet akışı",
        cta_primary="Teklif iste",
        cta_secondary="WhatsApp",
        icon="shine",
    ),
}

CATEGORY_ALIASES = {
    "kuaför": "kuafor",
    "güzellik salonu": "guzellik salonu",
    "oto yıkama": "oto yikama",
    "halı yıkama": "hali yikama",
    "çiçekçi": "cicekci",
    "pet kuaförü": "pet kuaforu",
    "özel kurs": "ozel kurs",
    "temizlik firması": "temizlik firmasi",
}


class PageGenerator:
    def __init__(self, output_dir: Path, demo_assets_dir: Path | None = None) -> None:
        self.output_dir = output_dir
        self.demo_assets_dir = demo_assets_dir or Path(__file__).with_name("demo_assets")

    def generate(self, scored: ScoredCandidate) -> GeneratedPage:
        candidate = scored.candidate
        slug = f"{ascii_slug(candidate.name)}-{ascii_slug(candidate.place_id)}"
        page_dir = self.output_dir / "demos" / slug
        assets_dir = page_dir / "assets"
        page_path = page_dir / "index.html"

        brand_kit = build_brand_kit(scored, slug)
        prompt_manifest = build_prompt_manifest(scored, brand_kit)
        html_text = render_demo_html(scored, brand_kit)

        validation = validate_generated_html(html_text)
        if not validation.allowed:
            raise ValueError(f"Generated HTML failed compliance: {', '.join(validation.reasons)}")

        page_dir.mkdir(parents=True, exist_ok=True)
        assets_dir.mkdir(parents=True, exist_ok=True)
        asset_provenance = _materialize_visual_assets(
            scored,
            brand_kit,
            assets_dir,
            self.demo_assets_dir,
        )
        page_manifest = build_page_manifest(
            scored,
            slug,
            brand_kit,
            prompt_manifest,
            asset_provenance=asset_provenance,
        )

        brand_kit_path = page_dir / "brand-kit.json"
        prompt_manifest_path = page_dir / "image-prompts.json"
        page_manifest_path = page_dir / "page-manifest.json"

        brand_kit_path.write_text(json.dumps(brand_kit, ensure_ascii=False, indent=2), encoding="utf-8")
        prompt_manifest_path.write_text(json.dumps(prompt_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        page_manifest_path.write_text(json.dumps(page_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        page_path.write_text(html_text, encoding="utf-8")

        assets = {
            "brand_kit": str(brand_kit_path),
            "image_prompt_manifest": str(prompt_manifest_path),
            "page_manifest": str(page_manifest_path),
            "hero_image": str(assets_dir / "hero-desktop.png"),
            "hero_desktop": str(assets_dir / "hero-desktop.png"),
            "hero_mobile": str(assets_dir / "hero-mobile.png"),
        }
        return GeneratedPage(
            place_id=candidate.place_id,
            path=page_path,
            slug=slug,
            package_dir=page_dir,
            assets=assets,
        )


def build_brand_kit(scored: ScoredCandidate, slug: str) -> dict:
    candidate = scored.candidate
    profile = _profile_for(candidate.category)
    ink, paper, accent, accent_2 = _palette_for(candidate.place_id, profile.palette)
    initials = _initials(candidate.name)

    return {
        "business": {
            "place_id": candidate.place_id,
            "name": candidate.name,
            "category": candidate.category,
            "location": candidate.display_location,
            "source": candidate.source,
            "slug": slug,
        },
        "brand": {
            "palette": {
                "ink": ink,
                "paper": paper,
                "accent": accent,
                "accent_2": accent_2,
                "soft": _mix_hex(paper, accent, 0.12),
                "line": _mix_hex(ink, paper, 0.82),
            },
            "typography": {
                "display": "Inter Tight, ui-sans-serif, system-ui",
                "body": "Inter, ui-sans-serif, system-ui",
                "scale_strategy": profile.type_scale,
            },
            "tone": profile.tone,
            "category": candidate.category,
            "visual_direction": profile.visual_direction,
            "cta_strategy": {
                "primary": profile.cta_primary,
                "secondary": profile.cta_secondary,
                "safe_language": [
                    "mobil uyumlu önizleme",
                    "yerel SEO'ya hazır teknik altyapı",
                    "hızlı açılan modern sayfa",
                    "işletme onayıyla düzenlenebilir içerik",
                ],
            },
        },
        "logo_analysis": {
            "source": "no_official_logo_available_in_mock_or_allowed_provider_fields",
            "derived_from": ["business_name", "category", "location"],
            "demo_mark": {
                "initials": initials,
                "strategy": "Özgün demo marka işareti; resmi logo gibi davranmaz ve işletme onayı olmadan yayın markası olarak kullanılmaz.",
            },
        },
        "compliance": {
            "noindex_required": True,
            "official_site_disclaimer_required": True,
            "reviews": "Yorum metinleri kopyalanmadı, saklanmadı veya alıntılanmadı.",
            "regulated_categories": "İlk hedef kategori seti dışında kalan ve regülasyonlu alanlar elenir.",
        },
    }


def build_visual_assets(scored: ScoredCandidate, brand_kit: dict) -> dict[str, bytes]:
    """Build deterministic raster placeholders for missing packaged imagery.

    Production-ready synthetic images can be packaged at
    ``demo_assets/<place_id>/hero-desktop.png`` and ``hero-mobile.png``. The
    generator copies those files verbatim when present. If only one packaged
    slot exists it is reused as the other slot and cropped by ``object-fit``;
    if neither exists a neutral raster placeholder keeps the page renderable.
    The fallback does not pretend to be a real photo and deliberately avoids
    inline SVG, icon sprites, and CSS artwork.
    """

    del scored  # The fallback is intentionally identity-free.
    palette = brand_kit["brand"]["palette"]
    return {
        "hero-desktop.png": _fallback_png(96, 60, palette, mobile=False),
        "hero-mobile.png": _fallback_png(60, 84, palette, mobile=True),
    }


def _materialize_visual_assets(
    scored: ScoredCandidate,
    brand_kit: dict,
    assets_dir: Path,
    demo_assets_dir: Path,
) -> dict[str, str]:
    fallbacks = build_visual_assets(scored, brand_kit)
    source_dir = _safe_place_asset_dir(demo_assets_dir, scored.candidate.place_id)
    provenance: dict[str, str] = {}
    source_files = {
        filename: source_dir / filename if source_dir is not None else None
        for filename in fallbacks
    }

    for filename, fallback in fallbacks.items():
        source = source_files[filename]
        target = assets_dir / filename
        if source is not None and _is_png(source):
            shutil.copy2(source, target)
            provenance[filename] = f"packaged_demo_asset:{scored.candidate.place_id}/{filename}"
            continue

        sibling_name = "hero-mobile.png" if filename == "hero-desktop.png" else "hero-desktop.png"
        sibling = source_files[sibling_name]
        if sibling is not None and _is_png(sibling):
            shutil.copy2(sibling, target)
            provenance[filename] = f"reused_packaged_demo_asset:{scored.candidate.place_id}/{sibling_name}"
            continue

        target.write_bytes(fallback)
        provenance[filename] = "deterministic_raster_fallback"
    return provenance


def _safe_place_asset_dir(root: Path, place_id: str) -> Path | None:
    clean_id = place_id.strip()
    if not clean_id or clean_id in {".", ".."} or "/" in clean_id or "\\" in clean_id:
        return None

    root_resolved = root.resolve()
    candidate = (root_resolved / clean_id).resolve()
    if candidate.parent != root_resolved:
        return None
    return candidate


def _is_png(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        with path.open("rb") as handle:
            return handle.read(8) == b"\x89PNG\r\n\x1a\n"
    except OSError:
        return False


def _fallback_png(width: int, height: int, palette: dict, *, mobile: bool) -> bytes:
    """Create a small text-free RGB PNG used only when a photo slot is absent."""

    ink = _hex_to_rgb(palette["ink"])
    accent = _hex_to_rgb(palette["accent"])
    paper = _hex_to_rgb(palette["paper"])
    rows: list[bytes] = []

    for y in range(height):
        row = bytearray([0])  # PNG filter type: none.
        vertical = y / max(1, height - 1)
        for x in range(width):
            horizontal = x / max(1, width - 1)
            sweep = (vertical * 0.72 + horizontal * (0.28 if mobile else 0.5)) / (1.0 if mobile else 1.22)
            base = tuple(round(ink[channel] * (1 - sweep) + accent[channel] * sweep) for channel in range(3))
            distance = ((horizontal - 0.72) ** 2 + (vertical - 0.24) ** 2) ** 0.5
            light = max(0.0, 0.22 - distance) * 1.4
            pixel = tuple(round(base[channel] * (1 - light) + paper[channel] * light) for channel in range(3))
            row.extend(pixel)
        rows.append(bytes(row))

    raw = b"".join(rows)
    signature = b"\x89PNG\r\n\x1a\n"
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return signature + _png_chunk(b"IHDR", header) + _png_chunk(b"IDAT", zlib.compress(raw, 9)) + _png_chunk(b"IEND", b"")


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    checksum = zlib.crc32(kind)
    checksum = zlib.crc32(payload, checksum) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", checksum)


def build_prompt_manifest(scored: ScoredCandidate, brand_kit: dict) -> dict:
    candidate = scored.candidate
    profile = _profile_for(candidate.category)
    palette = brand_kit["brand"]["palette"]
    source_signals = [
        "name",
        "category",
        "city",
        "district",
        "phone_presence",
        "website_status",
        "aggregate_rating_count_bucket",
    ]

    return {
        "mode": "packaged_raster_assets_with_safe_fallback",
        "note": (
            "PageGenerator önce paket içindeki demo_assets/<place_id>/hero-desktop.png ve hero-mobile.png "
            "dosyalarını arar. Tek slot varsa mevcut PNG diğer responsive slot için güvenle yeniden kullanılır; "
            "iki slot da yoksa sayfanın kırılmaması için logosuz, yazısız ve kimlik iddiası taşımayan "
            "deterministik bir PNG renk alanı kullanılır. Aşağıdaki promptlar iki slotun da yüksek kaliteli "
            "sentetik fotoğraflarla değiştirilmesi için hazırdır."
        ),
        "source_signals": source_signals,
        "safety_notes": [
            "Logo veya resmi marka varlığı kullanılmadı.",
            "Yorum metni, ham Google cevabı veya kişisel veri saklanmadı.",
            "Görseller işletmenin gerçek mekanı gibi sunulmaz; demo atmosfer assetidir.",
            "Attribution gerektiren Places Photo akışı kullanılmadı.",
            TURKISH_UI_TEXT_RULE,
        ],
        "copy_quality_notes": [
            "Görsel içinde Türkçe metin gerekiyorsa Türkçe karakterler korunur.",
            "ASCII'ye dönüşmüş Türkçe kelimeler kalite hatası sayılır.",
        ],
        "prompts": [
            {
                "id": "hero-desktop",
                "purpose": "Geniş ekrandaki split veya editoryal hero alanı için kategoriye uygun atmosfer fotoğrafı",
                "output_path": "assets/hero-desktop.png",
                "prompt": (
                    f"Use case: ads-marketing. Asset type: local business landing page hero. "
                    f"Create a polished, brand-safe visual for a {candidate.category} in {candidate.display_location}. "
                    f"Scene/backdrop: {profile.visual_direction}. Style: editorial, modern, no visible signage, no logos, no text. "
                    f"Composition: wide 8:5 desktop image, one coherent photographic scene, calm negative space. "
                    f"Color palette: ink {palette['ink']}, paper {palette['paper']}, accent {palette['accent']}, secondary {palette['accent_2']}. "
                    f"{TURKISH_UI_TEXT_RULE} "
                    "Avoid: real business identity claims, review snippets, people with identifiable faces, watermarks, rankings or guarantees."
                ),
            },
            {
                "id": "hero-mobile",
                "purpose": "Telefon ekranındaki yeniden kadrajlanmış hero alanı için ayrı mobil atmosfer fotoğrafı",
                "output_path": "assets/hero-mobile.png",
                "prompt": (
                    f"Use case: ads-marketing. Asset type: mobile local business landing page hero. "
                    f"Create a portrait 5:7 companion photograph for a {candidate.category} in {candidate.display_location}. "
                    f"Scene/backdrop: {profile.visual_direction}. Preserve the same art direction as the desktop image, "
                    "but recompose the subject for a narrow phone viewport; no baked-in UI, split panels, logos, signage, or text. "
                    f"Color palette: ink {palette['ink']}, paper {palette['paper']}, accent {palette['accent']}, secondary {palette['accent_2']}. "
                    f"{TURKISH_UI_TEXT_RULE} "
                    "Avoid: real business identity claims, identifiable faces, watermarks, rankings or guarantees."
                ),
            },
        ],
    }


def build_page_manifest(
    scored: ScoredCandidate,
    slug: str,
    brand_kit: dict,
    prompt_manifest: dict,
    asset_provenance: dict[str, str] | None = None,
) -> dict:
    candidate = scored.candidate
    layout = layout_for_category(candidate.category)
    return {
        "place_id": candidate.place_id,
        "slug": slug,
        "score": scored.score,
        "selected": scored.eligible,
        "why_selected": scored.reasons,
        "website_status": scored.website_status,
        "used_data_fields": [
            "place_id",
            "name",
            "category",
            "city",
            "district",
            "phone",
            "website_url",
            "rating",
            "review_count",
            "source",
        ],
        "source_mode": candidate.source,
        "layout_family": layout.family,
        "layout_composition": layout.composition,
        "asset_paths": {
            "brand_kit": "brand-kit.json",
            "image_prompt_manifest": "image-prompts.json",
            "page_manifest": "page-manifest.json",
            "hero_image": "assets/hero-desktop.png",
            "hero_desktop": "assets/hero-desktop.png",
            "hero_mobile": "assets/hero-mobile.png",
        },
        "asset_provenance": asset_provenance
        or {
            "hero-desktop.png": "deterministic_raster_fallback",
            "hero-mobile.png": "deterministic_raster_fallback",
        },
        "image_prompt_ids": [item["id"] for item in prompt_manifest["prompts"]],
        "avoidance_and_compliance_notes": [
            "robots noindex,nofollow,noarchive meta etiketi zorunlu tutuldu.",
            "SiteKapında önizleme uyarısı ve işletme sahibi onayı uyarısı eklendi.",
            "Sonuç garantisi, sıralama vaadi veya benzeri yasak iddialar kullanılmadı.",
            "Yorum metni kopyalanmadı, sayfaya alıntı olarak konmadı ve raw provider payload saklanmadı.",
            brand_kit["logo_analysis"]["demo_mark"]["strategy"],
        ],
    }


def render_demo_html(scored: ScoredCandidate, brand_kit: dict | None = None) -> str:
    candidate = scored.candidate
    brand = brand_kit or build_brand_kit(scored, f"{ascii_slug(candidate.name)}-{ascii_slug(candidate.place_id)}")
    profile = _profile_for(candidate.category)
    layout = layout_for_category(candidate.category)
    palette = brand["brand"]["palette"]

    name = html.escape(candidate.name)
    category = html.escape(candidate.category.title())
    location = html.escape(candidate.display_location)
    phone = normalize_phone(candidate.phone)
    phone_display = html.escape(candidate.phone or "İşletme onayı sonrası eklenecek")
    if candidate.source == "synthetic_fixture":
        # Judge fixtures must never look capable of contacting a real recipient.
        tel_href = "#contact"
        whatsapp_href = "#contact"
    else:
        tel_href = f"tel:{phone}" if phone else "#contact"
        whatsapp_href = f"https://wa.me/{phone.replace('+', '')}" if phone else "#contact"
    trust_points = "\n".join(
        f'<div><span>{index:02d}</span><strong>{html.escape(item)}</strong></div>'
        for index, item in enumerate(layout.trust_points, start=1)
    )
    sector_sections = _render_sector_sections(layout, profile)
    family = html.escape(layout.family)
    composition = html.escape(layout.composition)

    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow,noarchive">
  <title>{name} | SiteKapında Demo Önizleme</title>
  <style>
    :root {{
      --ink: {palette["ink"]};
      --paper: {palette["paper"]};
      --accent: {palette["accent"]};
      --accent-2: {palette["accent_2"]};
      --soft: {palette["soft"]};
      --line: {palette["line"]};
      --white: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; background: var(--paper); }}
    body {{
      margin: 0;
      color: var(--ink);
      background: var(--paper);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
      -webkit-font-smoothing: antialiased;
    }}
    a {{ color: inherit; text-decoration: none; }}
    img {{ display: block; max-width: 100%; }}
    .skip-link {{
      position: fixed;
      left: 1rem;
      top: 1rem;
      z-index: 99;
      padding: 0.75rem 1rem;
      background: var(--white);
      color: var(--ink);
      transform: translateY(-180%);
    }}
    .skip-link:focus {{ transform: translateY(0); }}
    .demo-strip {{
      background: var(--ink);
      color: var(--paper);
      font-size: 0.72rem;
      font-weight: 750;
      letter-spacing: 0.06em;
      padding: 0.65rem 4.5vw;
      text-align: center;
    }}
    .site-header {{
      min-height: 84px;
      display: grid;
      grid-template-columns: minmax(12rem, 1fr) auto minmax(12rem, 1fr);
      align-items: center;
      gap: 2rem;
      padding: 0 4.5vw;
      border-bottom: 1px solid var(--line);
      background: color-mix(in srgb, var(--paper) 94%, white);
    }}
    .wordmark {{
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(1.45rem, 2.4vw, 2.35rem);
      font-weight: 600;
      letter-spacing: -0.035em;
      line-height: 1;
    }}
    .desktop-nav {{ display: flex; align-items: center; gap: clamp(1.25rem, 3vw, 3rem); }}
    .desktop-nav a, .mobile-nav a {{
      min-height: 44px;
      display: inline-flex;
      align-items: center;
      font-size: 0.75rem;
      font-weight: 800;
      letter-spacing: 0.1em;
      text-transform: uppercase;
    }}
    .desktop-nav a:hover, .desktop-nav a:focus-visible {{ color: var(--accent); }}
    .header-cta {{ justify-self: end; }}
    .mobile-menu {{ display: none; justify-self: end; position: relative; }}
    .mobile-menu summary {{
      min-width: 64px;
      min-height: 44px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border: 1px solid var(--line);
      cursor: pointer;
      font-size: 0.75rem;
      font-weight: 850;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      list-style: none;
    }}
    .mobile-menu summary::-webkit-details-marker {{ display: none; }}
    .mobile-nav {{
      position: absolute;
      top: calc(100% + 0.5rem);
      right: 0;
      z-index: 20;
      width: min(18rem, calc(100vw - 2rem));
      display: grid;
      padding: 0.65rem 1rem;
      background: var(--paper);
      border: 1px solid var(--line);
      box-shadow: 0 18px 44px rgba(0, 0, 0, 0.14);
    }}
    .hero {{
      min-height: min(760px, calc(100svh - 118px));
      display: grid;
      grid-template-columns: minmax(0, 1.02fr) minmax(0, 0.98fr);
      border-bottom: 1px solid var(--line);
      overflow: hidden;
    }}
    .hero-copy {{
      min-height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: flex-start;
      padding: clamp(3.5rem, 7vw, 8rem) clamp(2rem, 6vw, 7rem) clamp(3.5rem, 7vw, 8rem) 4.5vw;
      animation: hero-rise 600ms cubic-bezier(.2,.7,.2,1) both;
    }}
    .hero-media {{ min-height: 100%; display: block; overflow: hidden; animation: hero-reveal 760ms ease both; }}
    .hero-media img {{ width: 100%; height: 100%; object-fit: cover; }}
    .hero--editorial {{ grid-template-columns: minmax(0, .9fr) minmax(0, 1.1fr); }}
    .hero--editorial .hero-media, .hero--botanical .hero-media {{ order: -1; }}
    .hero--portrait {{ grid-template-columns: minmax(0, 1.12fr) minmax(22rem, .88fr); }}
    .hero--workshop .hero-copy, .hero--technical .hero-copy, .hero--kinetic .hero-copy {{
      background: var(--ink);
      color: var(--paper);
    }}
    .hero--calm .hero-copy {{ background: var(--soft); }}
    .hero--academic .hero-copy {{ border-top: 8px solid var(--accent); }}
    .eyebrow {{
      margin: 0 0 1.3rem;
      color: var(--accent);
      font-size: 0.75rem;
      font-weight: 850;
      letter-spacing: 0.13em;
      text-transform: uppercase;
    }}
    h1, h2, h3 {{ font-family: Georgia, "Times New Roman", serif; font-weight: 500; }}
    h1 {{
      max-width: 12ch;
      margin: 0;
      font-size: clamp(3.5rem, 7vw, 7.8rem);
      line-height: 0.86;
      letter-spacing: -0.055em;
    }}
    .hero-statement {{
      max-width: 22ch;
      margin: 2rem 0 0;
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(1.45rem, 2.25vw, 2.6rem);
      line-height: 1.12;
      letter-spacing: -0.025em;
    }}
    .hero-description {{
      max-width: 37rem;
      margin: 1.25rem 0 0;
      color: color-mix(in srgb, currentColor 72%, transparent);
      font-size: clamp(1rem, 1.25vw, 1.14rem);
    }}
    .actions {{
      display: flex;
      gap: 0.75rem;
      flex-wrap: wrap;
      margin-top: 2rem;
    }}
    .button {{
      display: inline-flex;
      min-height: 48px;
      align-items: center;
      justify-content: center;
      padding: 0.78rem 1.25rem;
      border: 1px solid currentColor;
      font-size: 0.76rem;
      font-weight: 850;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      transition: transform 160ms ease, background 160ms ease, color 160ms ease;
      white-space: nowrap;
    }}
    .button.primary {{
      background: var(--accent);
      color: var(--white);
      border-color: var(--accent);
    }}
    .button:hover, .button:focus-visible {{ transform: translateY(-2px); }}
    .trust-strip {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      padding: 0 4.5vw;
      background: var(--soft);
      border-bottom: 1px solid var(--line);
    }}
    .trust-strip div {{
      min-height: 118px;
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 1.5rem clamp(1rem, 3vw, 3rem);
      border-right: 1px solid var(--line);
    }}
    .trust-strip div:last-child {{ border-right: 0; }}
    .trust-strip span {{ color: var(--accent); font-size: 0.68rem; font-weight: 900; }}
    .trust-strip strong {{ font-family: Georgia, "Times New Roman", serif; font-size: clamp(1.3rem, 2vw, 2rem); font-weight: 500; }}
    .sector {{ padding: clamp(5rem, 9vw, 9rem) 4.5vw; border-bottom: 1px solid var(--line); }}
    .section-heading {{
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(18rem, .85fr);
      gap: clamp(2rem, 8vw, 8rem);
      align-items: end;
      margin-bottom: clamp(3rem, 6vw, 5.5rem);
    }}
    h2 {{
      max-width: 16ch;
      margin: 0;
      font-size: clamp(2.8rem, 5.5vw, 6.5rem);
      line-height: 0.94;
      letter-spacing: -0.045em;
    }}
    .section-heading > p, .detail-copy {{ margin: 0; color: color-mix(in srgb, var(--ink) 67%, white); font-size: 1.04rem; }}
    .menu-lines, .service-index, .service-ledger, .collection-list, .schedule-list, .curriculum, .detail-list, .process-list {{
      list-style: none;
      padding: 0;
      margin: 0;
    }}
    .menu-lines, .service-index {{ display: grid; grid-template-columns: repeat(2, 1fr); border-top: 1px solid var(--line); }}
    .menu-lines li, .service-index li {{
      min-height: 210px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 2rem;
      padding: 1.5rem clamp(1.25rem, 3vw, 3rem);
      border-right: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
    }}
    .menu-lines li:nth-child(2n), .service-index li:nth-child(2n) {{ border-right: 0; }}
    .item-number {{ color: var(--accent); font-size: 0.7rem; font-weight: 900; letter-spacing: 0.1em; }}
    .item-title {{ font-family: Georgia, "Times New Roman", serif; font-size: clamp(1.75rem, 3vw, 3.2rem); line-height: 1; }}
    .item-note {{ color: color-mix(in srgb, var(--ink) 58%, white); font-size: .86rem; }}
    .sector-story, .sector-studio, .sector-care {{ background: var(--soft); }}
    .story-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(20rem, .72fr);
      gap: clamp(3rem, 10vw, 10rem);
      align-items: start;
    }}
    .story-grid h2 {{ margin-bottom: 2rem; }}
    .detail-list li, .service-ledger li, .schedule-list li {{
      min-height: 70px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1.5rem;
      padding: 1rem 0;
      border-bottom: 1px solid var(--line);
      font-weight: 750;
    }}
    .detail-list span, .service-ledger span, .schedule-list span {{ color: var(--accent); font-size: .7rem; font-weight: 900; }}
    .process-list, .collection-list, .curriculum {{ display: grid; grid-template-columns: repeat(3, 1fr); border-top: 1px solid var(--line); }}
    .process-list li, .collection-list li, .curriculum li {{
      min-height: 260px;
      padding: 1.75rem clamp(1.25rem, 3vw, 3rem);
      border-right: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
    }}
    .process-list li:last-child, .collection-list li:last-child, .curriculum li:last-child {{ border-right: 0; }}
    .process-list strong, .collection-list strong, .curriculum strong {{
      display: block;
      margin-top: 5rem;
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(1.7rem, 2.6vw, 2.8rem);
      font-weight: 500;
      line-height: 1.05;
    }}
    .service-ledger {{ border-top: 1px solid var(--line); }}
    .service-ledger strong {{ font-family: Georgia, "Times New Roman", serif; font-size: clamp(1.3rem, 2vw, 2rem); font-weight: 500; }}
    .care-list {{ margin: 0; border-top: 1px solid var(--line); }}
    .care-list div {{
      display: grid;
      grid-template-columns: 3rem minmax(0, 1fr) minmax(12rem, .7fr);
      gap: 1.5rem;
      align-items: center;
      padding: 1.4rem 0;
      border-bottom: 1px solid var(--line);
    }}
    .care-list dt {{ font-family: Georgia, "Times New Roman", serif; font-size: clamp(1.4rem, 2.3vw, 2.4rem); }}
    .care-list dd {{ margin: 0; color: color-mix(in srgb, var(--ink) 60%, white); }}
    .schedule-list {{ display: grid; grid-template-columns: repeat(3, 1fr); border-top: 1px solid var(--line); }}
    .schedule-list li {{ min-height: 150px; display: flex; flex-direction: column; align-items: flex-start; justify-content: space-between; padding: 1.5rem; border-right: 1px solid var(--line); }}
    .schedule-list li:last-child {{ border-right: 0; }}
    .schedule-list strong {{ font-family: Georgia, "Times New Roman", serif; font-size: 1.8rem; font-weight: 500; }}
    .final-cta {{
      min-height: 500px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: clamp(5rem, 9vw, 9rem) 4.5vw;
      background: var(--ink);
      color: var(--paper);
      text-align: center;
    }}
    .final-cta h2 {{ max-width: 14ch; }}
    .final-cta p {{ max-width: 42rem; margin: 1.75rem auto 0; color: color-mix(in srgb, var(--paper) 70%, transparent); }}
    .final-cta .actions {{ justify-content: center; }}
    .contact-line {{
      width: min(760px, 100%);
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
      margin-top: 2.5rem;
      padding-top: 1.5rem;
      border-top: 1px solid color-mix(in srgb, var(--paper) 24%, transparent);
      font-size: .85rem;
    }}
    .contact-line span:last-child {{ text-align: right; }}
    .site-footer {{
      display: grid;
      grid-template-columns: minmax(12rem, .7fr) minmax(0, 1.3fr);
      gap: 3rem;
      align-items: start;
      padding: 3rem 4.5vw;
      background: color-mix(in srgb, var(--ink) 94%, black);
      color: var(--paper);
    }}
    .site-footer p {{ max-width: 64rem; margin: 0; color: color-mix(in srgb, var(--paper) 65%, transparent); font-size: .78rem; }}
    @keyframes hero-rise {{ from {{ opacity: 0; transform: translateY(18px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes hero-reveal {{ from {{ opacity: .55; transform: scale(1.015); }} to {{ opacity: 1; transform: scale(1); }} }}
    :focus-visible {{ outline: 3px solid var(--accent-2); outline-offset: 3px; }}
    @media (max-width: 980px) {{
      .site-header {{ grid-template-columns: 1fr auto; min-height: 74px; }}
      .desktop-nav, .header-cta {{ display: none; }}
      .mobile-menu {{ display: block; }}
      .hero, .hero--editorial, .hero--portrait {{ grid-template-columns: minmax(0, .95fr) minmax(0, 1.05fr); }}
      .section-heading, .story-grid {{ grid-template-columns: 1fr; gap: 2rem; align-items: start; }}
      .process-list, .collection-list, .curriculum, .schedule-list {{ grid-template-columns: 1fr; }}
      .process-list li, .collection-list li, .curriculum li, .schedule-list li {{ min-height: 190px; border-right: 0; }}
      .process-list strong, .collection-list strong, .curriculum strong {{ margin-top: 3rem; }}
    }}
    @media (max-width: 720px) {{
      .demo-strip {{ padding-inline: 1rem; font-size: .64rem; }}
      .site-header {{ padding-inline: 1rem; }}
      .wordmark {{ font-size: 1.5rem; }}
      .hero, .hero--editorial, .hero--portrait {{ min-height: 0; grid-template-columns: 1fr; }}
      .hero-copy, .hero--editorial .hero-copy, .hero--portrait .hero-copy {{ order: 2; padding: 3.75rem 1rem 4.5rem; }}
      .hero-media, .hero--editorial .hero-media, .hero--botanical .hero-media {{ order: 1; min-height: 0; height: min(48svh, 420px); }}
      .hero--split .hero-copy {{ order: 1; padding-block: 3rem; }}
      .hero--split .hero-media {{ order: 2; }}
      h1 {{ font-size: clamp(3.25rem, 17vw, 5.5rem); }}
      .hero-statement {{ font-size: 1.55rem; }}
      .actions {{ width: 100%; flex-direction: column; }}
      .button {{ width: 100%; min-height: 48px; }}
      .trust-strip {{ grid-template-columns: 1fr; padding-inline: 1rem; }}
      .trust-strip div {{ min-height: 82px; padding-inline: 0; border-right: 0; border-bottom: 1px solid var(--line); }}
      .trust-strip div:last-child {{ border-bottom: 0; }}
      .sector {{ padding: 5rem 1rem; }}
      .section-heading {{ margin-bottom: 3rem; }}
      h2 {{ font-size: clamp(2.7rem, 13vw, 4.5rem); }}
      .menu-lines, .service-index {{ grid-template-columns: 1fr; }}
      .menu-lines li, .service-index li {{ min-height: 170px; padding-inline: 0; border-right: 0; }}
      .care-list div {{ grid-template-columns: 2.2rem 1fr; }}
      .care-list dd {{ grid-column: 2; }}
      .final-cta {{ min-height: 0; padding: 5.5rem 1rem; }}
      .contact-line, .site-footer {{ grid-template-columns: 1fr; }}
      .contact-line span:last-child {{ text-align: left; }}
      .site-footer {{ gap: 1.5rem; padding: 2.5rem 1rem; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      html {{ scroll-behavior: auto; }}
      *, *::before, *::after {{ animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; }}
    }}
  </style>
</head>
<body data-layout-family="{family}" data-layout-composition="{composition}">
  <a class="skip-link" href="#content">İçeriğe geç</a>
  <div class="demo-strip" role="note">Bu sayfa SiteKapında tarafından hazırlanmış bir önizleme sayfasıdır. İşletme sahibinin onayı olmadan resmi site olarak yayına alınmayacaktır.</div>
  <header class="site-header">
    <a class="wordmark" href="#top" aria-label="{name} ana sayfa">{name}</a>
    <nav class="desktop-nav" aria-label="Ana menü">
      <a href="#services">Hizmetler</a>
      <a href="#story">{html.escape(layout.nav_middle)}</a>
      <a href="#contact">İletişim</a>
    </nav>
    <a class="button primary header-cta" href="{tel_href}">{html.escape(profile.cta_secondary)}</a>
    <details class="mobile-menu">
      <summary>Menü</summary>
      <nav class="mobile-nav" aria-label="Mobil menü">
        <a href="#services">Hizmetler</a>
        <a href="#story">{html.escape(layout.nav_middle)}</a>
        <a href="#contact">İletişim</a>
      </nav>
    </details>
  </header>
  <main id="content">
    <section class="hero hero--{html.escape(layout.hero_variant)}" id="top">
      <div class="hero-copy">
        <p class="eyebrow">{html.escape(layout.eyebrow)} · {location}</p>
        <h1>{name}</h1>
        <p class="hero-statement">{html.escape(layout.hero_title)}</p>
        <p class="hero-description">{html.escape(layout.hero_copy)}</p>
        <div class="actions">
          <a class="button primary" href="{whatsapp_href}">{html.escape(profile.cta_primary)}</a>
          <a class="button" href="#services">Hizmetleri incele</a>
        </div>
      </div>
      <picture class="hero-media">
        <source media="(max-width: 720px)" srcset="assets/hero-mobile.png">
        <img src="assets/hero-desktop.png" alt="{category} için oluşturulmuş hakları güvenli demo atmosfer görseli" width="1600" height="1000" fetchpriority="high">
      </picture>
    </section>
    <section class="trust-strip" aria-label="Öne çıkan bilgiler">
      {trust_points}
    </section>
    {sector_sections}
    <section class="final-cta" id="contact">
      <p class="eyebrow">{category} · {location}</p>
      <h2>{html.escape(layout.cta_title)}</h2>
      <p>{html.escape(layout.cta_copy)}</p>
      <div class="actions">
        <a class="button primary" href="{whatsapp_href}">{html.escape(profile.cta_primary)}</a>
        <a class="button" href="{tel_href}">{html.escape(profile.cta_secondary)}</a>
      </div>
      <div class="contact-line"><span>{location}</span><span>{phone_display}</span></div>
    </section>
  </main>
  <footer class="site-footer">
    <span class="wordmark">{name}</span>
    <p>SiteKapında demo uyarısı: Bu önizleme satış görüşmesi için hazırlanmış kurgusal bir taslaktır ve işletme sahibinin onayı olmadan resmi site olarak yayına alınmaz. Fotoğraflar, metinler, hizmetler ve iletişim bilgileri yayın öncesinde işletme sahibiyle birlikte doğrulanır; yorum içeriği, sıralama vaadi veya sonuç garantisi kullanılmaz. Sayfa noindex,nofollow olarak tutulur.</p>
  </footer>
</body>
</html>
"""


def _render_sector_sections(layout: DemoLayout, profile: CategoryProfile) -> str:
    def heading(eyebrow: str, title: str, copy: str) -> str:
        return (
            '<div class="section-heading">'
            f'<div><p class="eyebrow">{html.escape(eyebrow)}</p><h2>{html.escape(title)}</h2></div>'
            f"<p>{html.escape(copy)}</p>"
            "</div>"
        )

    service_rows = "\n".join(
        (
            f'<li><span class="item-number">{index:02d}</span>'
            f'<strong class="item-title">{html.escape(service)}</strong>'
            f'<span class="item-note">{html.escape(profile.proof_points[(index - 1) % len(profile.proof_points)])}</span></li>'
        )
        for index, service in enumerate(profile.services, start=1)
    )
    ledger_rows = "\n".join(
        f'<li><strong>{html.escape(service)}</strong><span>{index:02d}</span></li>'
        for index, service in enumerate(profile.services, start=1)
    )
    detail_rows = "\n".join(
        f'<li><span>{index:02d}</span><strong>{html.escape(item)}</strong></li>'
        for index, item in enumerate(layout.detail_items, start=1)
    )
    process_rows = "\n".join(
        f'<li><span class="item-number">{index:02d}</span><strong>{html.escape(item)}</strong></li>'
        for index, item in enumerate(layout.detail_items, start=1)
    )

    if layout.composition == "menu-story":
        return f"""
    <section class="sector sector-menu" id="services">
      {heading(layout.section_eyebrow, layout.section_title, layout.section_copy)}
      <ol class="menu-lines">{service_rows}</ol>
    </section>
    <section class="sector sector-story" id="story">
      <div class="story-grid">
        <div><p class="eyebrow">{html.escape(layout.detail_eyebrow)}</p><h2>{html.escape(layout.detail_title)}</h2><p class="detail-copy">{html.escape(layout.detail_copy)}</p></div>
        <ul class="detail-list">{detail_rows}</ul>
      </div>
    </section>"""

    if layout.composition == "editorial-services":
        return f"""
    <section class="sector sector-editorial" id="services">
      {heading(layout.section_eyebrow, layout.section_title, layout.section_copy)}
      <ol class="service-index">{service_rows}</ol>
    </section>
    <section class="sector sector-studio" id="story">
      <div class="story-grid">
        <div><p class="eyebrow">{html.escape(layout.detail_eyebrow)}</p><h2>{html.escape(layout.detail_title)}</h2><p class="detail-copy">{html.escape(layout.detail_copy)}</p></div>
        <ul class="detail-list">{detail_rows}</ul>
      </div>
    </section>"""

    if layout.composition == "collection":
        return f"""
    <section class="sector sector-collection" id="services">
      {heading(layout.section_eyebrow, layout.section_title, layout.section_copy)}
      <ol class="collection-list">{process_rows}</ol>
    </section>
    <section class="sector sector-story" id="story">
      <div class="story-grid">
        <div><p class="eyebrow">{html.escape(layout.detail_eyebrow)}</p><h2>{html.escape(layout.detail_title)}</h2><p class="detail-copy">{html.escape(layout.detail_copy)}</p></div>
        <ul class="service-ledger">{ledger_rows}</ul>
      </div>
    </section>"""

    if layout.composition == "care-plan":
        care_rows = "\n".join(
            (
                f'<div><span class="item-number">{index:02d}</span>'
                f'<dt>{html.escape(service)}</dt>'
                f'<dd>{html.escape(profile.proof_points[(index - 1) % len(profile.proof_points)])}</dd></div>'
            )
            for index, service in enumerate(profile.services, start=1)
        )
        return f"""
    <section class="sector sector-care" id="services">
      {heading(layout.section_eyebrow, layout.section_title, layout.section_copy)}
      <dl class="care-list">{care_rows}</dl>
    </section>
    <section class="sector sector-process" id="story">
      {heading(layout.detail_eyebrow, layout.detail_title, layout.detail_copy)}
      <ol class="process-list">{process_rows}</ol>
    </section>"""

    if layout.composition == "schedule":
        return f"""
    <section class="sector sector-program" id="services">
      {heading(layout.section_eyebrow, layout.section_title, layout.section_copy)}
      <ul class="service-ledger">{ledger_rows}</ul>
    </section>
    <section class="sector sector-schedule" id="story">
      {heading(layout.detail_eyebrow, layout.detail_title, layout.detail_copy)}
      <ol class="schedule-list">{detail_rows}</ol>
    </section>"""

    if layout.composition == "curriculum":
        return f"""
    <section class="sector sector-curriculum" id="services">
      {heading(layout.section_eyebrow, layout.section_title, layout.section_copy)}
      <ul class="service-ledger">{ledger_rows}</ul>
    </section>
    <section class="sector sector-story" id="story">
      {heading(layout.detail_eyebrow, layout.detail_title, layout.detail_copy)}
      <ol class="curriculum">{process_rows}</ol>
    </section>"""

    return f"""
    <section class="sector sector-service" id="services">
      {heading(layout.section_eyebrow, layout.section_title, layout.section_copy)}
      <ul class="service-ledger">{ledger_rows}</ul>
    </section>
    <section class="sector sector-process" id="story">
      {heading(layout.detail_eyebrow, layout.detail_title, layout.detail_copy)}
      <ol class="process-list">{process_rows}</ol>
    </section>"""


def _profile_for(category: str) -> CategoryProfile:
    key = normalize_text(category)
    key = CATEGORY_ALIASES.get(key, key)
    return CATEGORY_PROFILES.get(key, DEFAULT_PROFILE)


def _palette_for(place_id: str, palette: tuple[str, str, str, str]) -> tuple[str, str, str, str]:
    digest = hashlib.sha256(place_id.encode("utf-8")).digest()
    if digest[0] % 3 == 0:
        return palette
    if digest[0] % 3 == 1:
        return (palette[0], _mix_hex(palette[1], "#ffffff", 0.24), palette[2], palette[3])
    return (palette[0], palette[1], _mix_hex(palette[2], palette[0], 0.14), palette[3])


def _initials(name: str) -> str:
    parts = [part for part in name.replace("&", " ").split() if part]
    if not parts:
        return "SK"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def _mix_hex(first: str, second: str, amount_second: float) -> str:
    amount_second = max(0, min(1, amount_second))
    r1, g1, b1 = _hex_to_rgb(first)
    r2, g2, b2 = _hex_to_rgb(second)
    r = round(r1 * (1 - amount_second) + r2 * amount_second)
    g = round(g1 * (1 - amount_second) + g2 * amount_second)
    b = round(b1 * (1 - amount_second) + b2 * amount_second)
    return f"#{r:02x}{g:02x}{b:02x}"


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)
