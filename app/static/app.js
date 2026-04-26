const { useMemo, useState, useEffect, useContext, createContext } = React;

const CURRENCY = new Intl.NumberFormat("en-US", { style: "currency", currency: "ILS" });
const STORAGE_KEY = "priceradar-tracked-products-v1";
const GSMARENA_IMAGE = (slug) => `https://fdn2.gsmarena.com/vv/bigpic/${slug}.jpg`;
const PRODUCT_IMAGE = (url) => url;
const SONY_WH1000XM5_IMAGE = PRODUCT_IMAGE("https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6505/6505727_rd.jpg%3BmaxHeight%3D1920%3BmaxWidth%3D900?format=webp");
const APPLE_WATCH_SE_IMAGE = PRODUCT_IMAGE("https://www.apple.com/newsroom/images/product/watch/lifestyle/Apple-Watch-SE-aluminum-midnight-220907_inline.jpg.large.jpg");
const MACBOOK_AIR_IMAGE = PRODUCT_IMAGE("https://www.apple.com/newsroom/images/2025/03/apple-introduces-the-new-macbook-air-with-the-m4-chip-and-a-sky-blue-color/article/Apple-MacBook-Air-sky-blue-250305_big.jpg.large.jpg");
const AIRPODS_PRO_2_IMAGE = PRODUCT_IMAGE("https://www.apple.com/newsroom/images/2023/09/apple-introduces-new-airpods-pro-2nd-generation/article/Apple-AirPods-Pro-2nd-generation-USB-C-connection-230912_inline.jpg.large.jpg");
const HOMEPOD_MINI_IMAGE = PRODUCT_IMAGE("https://www.apple.com/newsroom/images/2024/07/apple-introduces-homepod-mini-in-midnight/article/Apple-HomePod-mini-midnight_inline.jpg.large.jpg");
const PLAYSTATION_5_IMAGE = PRODUCT_IMAGE("https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6426/6426149_sd.jpg%3BmaxHeight%3D1920%3BmaxWidth%3D900?format=webp");
const NINJA_AIR_FRYER_IMAGE = PRODUCT_IMAGE("https://i02.hsncdn.com/is/image/HomeShoppingNetwork/rocs1200/ninja-air-fryer-max-xl-d-2025051617474669~23491946w.jpg");
const STEAM_DECK_OLED_IMAGE = PRODUCT_IMAGE("https://cdn.fastly.steamstatic.com/steamdeck/images/oled/oled_deck_top.png");
const SAMSUNG_GALAXY_S24_ULTRA_IMAGE = PRODUCT_IMAGE("https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6570/6570299_sd.jpg%3BmaxHeight%3D1920%3BmaxWidth%3D900?format=webp");
const GOOGLE_PIXEL_8_PRO_IMAGE = PRODUCT_IMAGE("https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6559/6559251_sd.jpg%3BmaxHeight%3D1920%3BmaxWidth%3D900?format=webp");
const SAMSUNG_GALAXY_Z_FLIP3_IMAGE = PRODUCT_IMAGE("https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6466/6466010_sd.jpg%3BmaxHeight%3D1920%3BmaxWidth%3D900?format=webp");
const SAMSUNG_GALAXY_TAB_S8_IMAGE = PRODUCT_IMAGE("https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6494/6494231_sd.jpg%3BmaxHeight%3D1920%3BmaxWidth%3D900?format=webp");
const DELL_XPS_13_IMAGE = PRODUCT_IMAGE("https://pisces.bbystatic.com/image2/BestBuy_US/images/products/c6db3d19-e7ba-4f81-89fb-d1857d5977b3.png%3BmaxHeight%3D1920%3BmaxWidth%3D900?format=webp");
const SURFACE_LAPTOP_IMAGE = PRODUCT_IMAGE("https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6623/6623675_sd.jpg%3BmaxHeight%3D1920%3BmaxWidth%3D900?format=webp");
const THINKPAD_X1_CARBON_IMAGE = PRODUCT_IMAGE("https://pisces.bbystatic.com/image2/BestBuy_US/images/products/852b0c1b-1a3e-4a15-ae09-f00d621cebc7.jpg%3BmaxHeight%3D1920%3BmaxWidth%3D900?format=webp");
const AIRPODS_MAX_IMAGE = PRODUCT_IMAGE("https://images.apple.com/v/airpods-max/k/images/overview/product-stories/hifi-sound/modal/audio_bc_microphone__c4kgd4pga3cm_large.png");
const BOSE_QC35_II_IMAGE = PRODUCT_IMAGE("https://pisces.bbystatic.com/image2/BestBuy_US/images/products/5876/5876115_sd.jpg%3BmaxHeight%3D1920%3BmaxWidth%3D900?format=webp");
const NINTENDO_SWITCH_OLED_IMAGE = PRODUCT_IMAGE("https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6470/6470923_sd.jpg%3BmaxHeight%3D1920%3BmaxWidth%3D900?format=webp");
const XBOX_SERIES_X_IMAGE = PRODUCT_IMAGE("https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6428/6428324_sd.jpg%3BmaxHeight%3D1920%3BmaxWidth%3D900?format=webp");
const SONY_WF1000XM4_IMAGE = PRODUCT_IMAGE("https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6462/6462204_sd.jpg%3BmaxHeight%3D1920%3BmaxWidth%3D900?format=webp");
const SURFACE_PRO_9_IMAGE = PRODUCT_IMAGE("https://support.microsoft.com/en-us/surface/media/surface-pro-9-back.png");
const STEAM_DECK_IMAGE = PRODUCT_IMAGE("https://cdn.fastly.steamstatic.com/steamdeck/images/deck/deck_top.png");
const GENERIC_PRODUCT_PLACEHOLDER = PRODUCT_IMAGE("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 520 520'><rect width='520' height='520' rx='40' fill='%23ffffff'/><rect x='70' y='90' width='380' height='260' rx='28' fill='%23f8fafc' stroke='%23dbeafe' stroke-width='8'/><rect x='112' y='132' width='296' height='176' rx='18' fill='%23e2e8f0'/><circle cx='160' cy='390' r='16' fill='%2394a3b8'/><rect x='192' y='372' width='168' height='18' rx='9' fill='%2394a3b8'/><rect x='192' y='402' width='116' height='18' rx='9' fill='%23cbd5e1'/></svg>");
const HERO_BACKGROUND_IMAGE = "/static/hero-background.png";

const PRODUCT_IMAGE_OVERRIDES = {
  "galaxy-s24-ultra": SAMSUNG_GALAXY_S24_ULTRA_IMAGE,
  "pixel-8-pro": GOOGLE_PIXEL_8_PRO_IMAGE,
  "galaxy-z-flip3": SAMSUNG_GALAXY_Z_FLIP3_IMAGE,
  "galaxy-tab-s8": SAMSUNG_GALAXY_TAB_S8_IMAGE,
};

const CATALOG = [
  { id: "iphone-15-pro", name: "iPhone 15 Pro", store: "KSP", category: "Smartphones", product_url: "https://example.com/iphone-15-pro", current_price: 4999, image: GSMARENA_IMAGE("apple-iphone-15-pro") },
  { id: "macbook-air", name: "MacBook Air", store: "iDigital", category: "Laptops", product_url: "https://example.com/macbook-air-13", current_price: 5590, image: MACBOOK_AIR_IMAGE },
  { id: "airpods-pro-2", name: "AirPods Pro (2nd generation)", store: "Ivory", category: "Audio", product_url: "https://example.com/airpods-pro-2", current_price: 989, image: AIRPODS_PRO_2_IMAGE },
  { id: "galaxy-s24-ultra", name: "Samsung Galaxy S24 Ultra", store: "Samsung Store", category: "Smartphones", product_url: "https://example.com/galaxy-s24-ultra", current_price: 4790, image: SAMSUNG_GALAXY_S24_ULTRA_IMAGE },
  { id: "homepod-mini", name: "Apple HomePod mini", store: "iStore", category: "Audio", product_url: "https://example.com/homepod-mini", current_price: 469, image: HOMEPOD_MINI_IMAGE },
  { id: "playstation-5", name: "PlayStation 5", store: "Bug", category: "Gaming", product_url: "https://example.com/playstation-5", current_price: 2399, image: PLAYSTATION_5_IMAGE },
  { id: "apple-watch-series-9", name: "Apple Watch Series 9", store: "iDigital", category: "Wearables", product_url: "https://example.com/apple-watch-series-9", current_price: 1799, image: GSMARENA_IMAGE("apple-watch-series-9") },
  { id: "ipad-mini-6", name: "iPad mini (6th generation)", store: "KSP", category: "Tablets", product_url: "https://example.com/ipad-mini-6", current_price: 2390, image: GSMARENA_IMAGE("apple-ipad-mini-2021") },
  { id: "pixel-8-pro", name: "Google Pixel 8 Pro", store: "Google Store", category: "Smartphones", product_url: "https://example.com/google-pixel-8-pro", current_price: 4290, image: GOOGLE_PIXEL_8_PRO_IMAGE },
  { id: "nothing-phone-2", name: "Nothing Phone (2)", store: "Nothing", category: "Smartphones", product_url: "https://example.com/nothing-phone-2", current_price: 2690, image: GSMARENA_IMAGE("nothing-phone2") },
  { id: "oneplus-open", name: "OnePlus Open", store: "OnePlus", category: "Smartphones", product_url: "https://example.com/oneplus-open", current_price: 5790, image: GSMARENA_IMAGE("oneplus-open") },
  { id: "xiaomi-13-ultra", name: "Xiaomi 13 Ultra", store: "Xiaomi", category: "Smartphones", product_url: "https://example.com/xiaomi-13-ultra", current_price: 4490, image: GSMARENA_IMAGE("xiaomi-13-ultra") },
  { id: "galaxy-z-flip3", name: "Samsung Galaxy Z Flip3", store: "Samsung Store", category: "Smartphones", product_url: "https://example.com/galaxy-z-flip3", current_price: 2390, image: SAMSUNG_GALAXY_Z_FLIP3_IMAGE },
  { id: "pixel-fold", name: "Google Pixel Fold", store: "Google Store", category: "Smartphones", product_url: "https://example.com/google-pixel-fold", current_price: 5490, image: GSMARENA_IMAGE("google-pixel-fold") },
  { id: "fairphone-5", name: "Fairphone 5", store: "Fairphone", category: "Smartphones", product_url: "https://example.com/fairphone-5", current_price: 2990, image: GSMARENA_IMAGE("fairphone-5") },
  { id: "dell-xps-13", name: "Dell XPS 13 (2018)", store: "Dell", category: "Laptops", product_url: "https://example.com/dell-xps-13", current_price: 5390, image: DELL_XPS_13_IMAGE },
  { id: "surface-laptop-go", name: "Microsoft Surface Laptop Go", store: "Microsoft Store", category: "Laptops", product_url: "https://example.com/surface-laptop-go", current_price: 3290, image: SURFACE_LAPTOP_IMAGE },
  { id: "thinkpad-x1-carbon", name: "Lenovo ThinkPad X1 Carbon", store: "Lenovo", category: "Laptops", product_url: "https://example.com/thinkpad-x1-carbon", current_price: 6190, image: THINKPAD_X1_CARBON_IMAGE },
  { id: "airpods-max", name: "AirPods Max", store: "Apple", category: "Audio", product_url: "https://example.com/airpods-max", current_price: 2190, image: AIRPODS_MAX_IMAGE },
  { id: "sony-wf-1000xm4", name: "Sony WF-1000XM4", store: "Sony", category: "Audio", product_url: "https://example.com/sony-wf-1000xm4", current_price: 899, image: SONY_WF1000XM4_IMAGE },
  { id: "bose-qc35-ii", name: "Bose QuietComfort 35 II", store: "Bose", category: "Audio", product_url: "https://example.com/bose-qc35-ii", current_price: 1190, image: BOSE_QC35_II_IMAGE },
  { id: "steam-deck", name: "Steam Deck", store: "Valve", category: "Gaming", product_url: "https://example.com/steam-deck", current_price: 2499, image: STEAM_DECK_IMAGE },
  { id: "nintendo-switch-oled", name: "Nintendo Switch OLED Model", store: "Nintendo", category: "Gaming", product_url: "https://example.com/nintendo-switch-oled", current_price: 1599, image: NINTENDO_SWITCH_OLED_IMAGE },
  { id: "xbox-series-x", name: "Xbox Series X", store: "Microsoft Store", category: "Gaming", product_url: "https://example.com/xbox-series-x", current_price: 2199, image: XBOX_SERIES_X_IMAGE },
  { id: "galaxy-tab-s8", name: "Samsung Galaxy Tab S8", store: "Samsung Store", category: "Tablets", product_url: "https://example.com/galaxy-tab-s8", current_price: 2790, image: SAMSUNG_GALAXY_TAB_S8_IMAGE },
  { id: "surface-pro-9", name: "Microsoft Surface Pro 9", store: "Microsoft Store", category: "Tablets", product_url: "https://example.com/surface-pro-9", current_price: 4890, image: SURFACE_PRO_9_IMAGE },
  { id: "galaxy-watch-4", name: "Samsung Galaxy Watch 4", store: "Samsung Store", category: "Wearables", product_url: "https://example.com/galaxy-watch-4", current_price: 799, image: GSMARENA_IMAGE("samsung-galaxy-watch4") },
  { id: "galaxy-watch-6", name: "Samsung Galaxy Watch 6", store: "Samsung Store", category: "Wearables", product_url: "https://example.com/galaxy-watch-6", current_price: 1099, image: GSMARENA_IMAGE("samsung-galaxy-watch6") },
];

const CATEGORIES = [
  { name: "Smartphones", slug: "smartphones", image: SAMSUNG_GALAXY_S24_ULTRA_IMAGE },
  { name: "Laptops", slug: "laptops", image: MACBOOK_AIR_IMAGE },
  { name: "Audio", slug: "audio", image: SONY_WH1000XM5_IMAGE },
  { name: "Gaming", slug: "gaming", image: PLAYSTATION_5_IMAGE },
  { name: "Wearables", slug: "wearables", image: APPLE_WATCH_SE_IMAGE },
  { name: "Tablets", slug: "tablets", image: SAMSUNG_GALAXY_TAB_S8_IMAGE },
];

const TRACKED_PRODUCT_OVERRIDES = [
  {
    match: /sony wh-1000xm5/i,
    category: "Audio",
    image: SONY_WH1000XM5_IMAGE,
  },
  {
    match: /apple watch se/i,
    category: "Wearables",
    image: APPLE_WATCH_SE_IMAGE,
  },
  {
    match: /ninja air fryer/i,
    category: "Home Appliances",
    image: NINJA_AIR_FRYER_IMAGE,
  },
  {
    match: /steam deck oled/i,
    category: "Gaming",
    image: STEAM_DECK_OLED_IMAGE,
  },
];

function imageOverrideFor(productLike) {
  if (!productLike) return null;
  const id = `${productLike.id || ""}`.trim();
  return PRODUCT_IMAGE_OVERRIDES[id] || null;
}

const AppContext = createContext(null);
const useApp = () => useContext(AppContext);

function makeWeekSeries(current, target) {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  return days.map((day, idx) => {
    const variance = ((idx - 3) * current * 0.01) + ((idx % 2 ? 1 : -1) * current * 0.006);
    return { day, price: Number((current + variance).toFixed(2)), target };
  });
}

function findCatalogProduct(productLike) {
  return (
    CATALOG.find((item) => item.product_url === productLike.product_url) ||
    CATALOG.find((item) => item.name === productLike.name) ||
    CATALOG.find((item) => item.id === productLike.id) ||
    null
  );
}

function categoryImageByName(name) {
  return CATEGORIES.find((category) => category.name === name)?.image || GENERIC_PRODUCT_PLACEHOLDER;
}

function findTrackedOverride(productLike) {
  const name = `${productLike.name || ""}`.trim();
  const url = `${productLike.product_url || ""}`.trim();
  return (
    TRACKED_PRODUCT_OVERRIDES.find((item) => item.match.test(name) || item.match.test(url)) ||
    null
  );
}

function enrichTrackedProduct(productLike) {
  const override = findTrackedOverride(productLike);
  const match = findCatalogProduct(productLike);
  const image = imageOverrideFor(productLike) || productLike.image || override?.image || imageOverrideFor(match) || match?.image || categoryImageByName(productLike.category);
  const category = productLike.category || override?.category || match?.category || "Tracked";
  return {
    ...productLike,
    image,
    category,
    history: makeWeekSeries(productLike.current_price, productLike.target_price),
    status: productLike.is_active ? (productLike.current_price <= productLike.target_price ? "price-dropped" : "tracking") : "paused",
  };
}

function displayImageFor(productLike) {
  const match = findCatalogProduct(productLike);
  return imageOverrideFor(productLike) || productLike?.image || imageOverrideFor(match) || match?.image || categoryImageByName(productLike?.category);
}

function fallbackImageFor(productLike) {
  return imageOverrideFor(productLike) || categoryImageByName(productLike?.category) || GENERIC_PRODUCT_PLACEHOLDER;
}

function AppProvider({ children }) {
  const [trackedProducts, setTrackedProducts] = useState(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  });
  const [toast, setToast] = useState(null);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(trackedProducts));
  }, [trackedProducts]);

  const refreshTrackedFromBackend = async () => {
    try {
      const response = await fetch("/products");
      const data = await response.json();
      if (!response.ok || !Array.isArray(data)) {
        throw new Error(data.detail || "Failed loading tracked products.");
      }
      setTrackedProducts(data.map(enrichTrackedProduct));
    } catch (error) {
      setToast({ type: "error", text: error.message });
    }
  };

  useEffect(() => {
    refreshTrackedFromBackend();
  }, []);

  const trackProduct = async (product, targetPrice, storeUrlInput) => {
    const target = Number(targetPrice);
    if (!target || target <= 0 || target > Number(product.current_price)) {
      setToast({ type: "error", text: "Target must be positive and lower than current price." });
      return false;
    }

    const name = (product.name || "").trim();
    const store = (product.store || "").trim();
    const productUrl = (storeUrlInput || "").trim() || (product.product_url || "").trim();
    const currentPrice = Number(product.current_price);

    if (!name || !store || !productUrl || !currentPrice) {
      setToast({ type: "error", text: "Name, store, URL and current price are required." });
      return false;
    }

    if (!productUrl.startsWith("http://") && !productUrl.startsWith("https://")) {
      setToast({ type: "error", text: "Store URL must start with http:// or https://." });
      return false;
    }

    const payload = {
      name,
      store,
      product_url: productUrl,
      current_price: currentPrice,
      target_price: target,
      currency: "ILS",
      is_active: true,
    };

    try {
      const res = await fetch("/products", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Could not save to backend.");
      }
      const item = enrichTrackedProduct({
        ...data,
        image: product.image,
        category: product.category,
      });
      setTrackedProducts((prev) => [item, ...prev]);
      setToast({ type: "success", text: `${product.name} tracked successfully.` });
      return true;
    } catch (err) {
      setToast({ type: "error", text: err.message || "Tracking failed." });
      return false;
    }
  };

  const pauseTracked = async (productId) => {
    const backup = trackedProducts;
    setTrackedProducts((prev) =>
      prev.map((p) => (p.id === productId ? { ...p, status: "paused", is_active: false } : p)),
    );
    try {
      const response = await fetch(`/products/${productId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: false }),
      });
      if (!response.ok) {
        throw new Error("Failed to pause");
      }
      setToast({ type: "success", text: "Tracking paused." });
    } catch (_error) {
      setTrackedProducts(backup);
      setToast({ type: "error", text: "Could not sync pause with backend." });
    }
  };

  const resumeTracked = async (productId) => {
    const backup = trackedProducts;
    setTrackedProducts((prev) =>
      prev.map((p) => (p.id === productId ? enrichTrackedProduct({ ...p, is_active: true }) : p)),
    );
    try {
      const response = await fetch(`/products/${productId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: true }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to resume");
      }
      setTrackedProducts((prev) =>
        prev.map((p) => (p.id === productId ? enrichTrackedProduct({ ...p, ...data }) : p)),
      );
      setToast({ type: "success", text: "Tracking resumed." });
    } catch (_error) {
      setTrackedProducts(backup);
      setToast({ type: "error", text: "Could not resume tracking." });
    }
  };

  const updateTrackedPricing = async (productId, nextCurrentPrice, nextTargetPrice) => {
    const current = trackedProducts.find((product) => product.id === productId);
    if (!current) {
      setToast({ type: "error", text: "Tracked product not found." });
      return false;
    }

    const currentPrice = Number(nextCurrentPrice);
    const targetPrice = Number(nextTargetPrice);
    if (!currentPrice || currentPrice <= 0 || !targetPrice || targetPrice <= 0) {
      setToast({ type: "error", text: "Current price and target price must be positive." });
      return false;
    }
    if (targetPrice > currentPrice) {
      setToast({ type: "error", text: "Target price must be lower than or equal to current price." });
      return false;
    }

    const backup = trackedProducts;
    setTrackedProducts((prev) =>
      prev.map((product) => (
        product.id === productId
          ? enrichTrackedProduct({ ...product, current_price: currentPrice, target_price: targetPrice })
          : product
      )),
    );

    try {
      const response = await fetch(`/products/${productId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          current_price: currentPrice,
          target_price: targetPrice,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed updating prices.");
      }
      setTrackedProducts((prev) =>
        prev.map((product) => (
          product.id === productId
            ? enrichTrackedProduct({ ...product, ...data })
            : product
        )),
      );
      setToast({ type: "success", text: "Tracked prices updated." });
      return true;
    } catch (error) {
      setTrackedProducts(backup);
      setToast({ type: "error", text: error.message || "Could not update prices." });
      return false;
    }
  };

  const removeTracked = async (productId) => {
    const backup = trackedProducts;
    setTrackedProducts((prev) => prev.filter((p) => p.id !== productId));
    try {
      const res = await fetch(`/products/${productId}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Delete failed");
      setToast({ type: "success", text: "Tracking removed." });
    } catch (_error) {
      setTrackedProducts(backup);
      setToast({ type: "error", text: "Could not delete from backend." });
    }
  };

  const exportCsv = () => {
    if (!trackedProducts.length) {
      setToast({ type: "error", text: "No tracked products to export." });
      return;
    }
    const header = ["name", "store", "product_url", "current_price", "target_price", "status"];
    const rows = trackedProducts.map((p) => [
      p.name,
      p.store,
      p.product_url,
      p.current_price,
      p.target_price,
      p.status,
    ]);
    const csv = [header, ...rows]
      .map((row) => row.map((v) => `"${String(v ?? "").replaceAll('"', '""')}"`).join(","))
      .join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "priceradar-tracked-products.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    setToast({ type: "success", text: "CSV exported." });
  };

  return (
    <AppContext.Provider
      value={{
        trackedProducts,
        trackProduct,
        pauseTracked,
        resumeTracked,
        updateTrackedPricing,
        removeTracked,
        exportCsv,
        refreshTrackedFromBackend,
        toast,
        setToast,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

function useHashRoute() {
  const [hash, setHash] = useState(window.location.hash || "#/");
  useEffect(() => {
    const onChange = () => setHash(window.location.hash || "#/");
    window.addEventListener("hashchange", onChange);
    if (!window.location.hash) {
      window.location.hash = "#/";
    }
    return () => window.removeEventListener("hashchange", onChange);
  }, []);
  return hash;
}

function navigateTo(path) {
  window.location.hash = `#${path}`;
}

function categoryPath(category) {
  return `/category/${category.slug}`;
}

function findCategoryBySlug(slug) {
  return CATEGORIES.find((category) => category.slug === slug) || null;
}

function TopNav() {
  const { trackedProducts } = useApp();
  const route = useHashRoute();
  const [showCategories, setShowCategories] = useState(false);
  const categoriesActive = route.startsWith("#/category/");
  const navClass = (path) =>
    `rounded-full px-4 py-1.5 text-sm transition ${
      route === `#${path}` ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-700"
    }`;
  return (
    <header className="sticky top-0 z-20 border-b border-zinc-200/70 bg-white/80 backdrop-blur">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-4">
        <button onClick={() => navigateTo("/")} className="group flex items-center gap-3">
          <div className="rounded-xl bg-blue-50 p-2 text-radarBlue transition group-hover:scale-105"><i data-lucide="radar" className="h-5 w-5" /></div>
          <div>
            <p className="text-lg font-bold tracking-tight">PriceRadar</p>
            <p className="text-xs text-slate-500">Premium Price Tracking</p>
          </div>
        </button>
        <nav className="flex items-center gap-2 rounded-full border border-zinc-200 bg-zinc-50 p-1">
          <div
            className="relative"
            onMouseEnter={() => setShowCategories(true)}
            onMouseLeave={() => setShowCategories(false)}
          >
            <button
              onClick={() => setShowCategories((current) => !current)}
              className={`rounded-full px-4 py-1.5 text-sm transition ${categoriesActive ? "bg-white text-slate-900 shadow-sm" : "text-slate-600 hover:text-slate-900"}`}
            >
              Categories
            </button>
            {showCategories && (
              <>
                <div className="absolute left-0 top-full z-20 h-3 w-80" />
                <div className="absolute left-0 top-[calc(100%+0.75rem)] z-30 w-80 rounded-2xl border border-zinc-200 bg-white p-3 shadow-xl">
                  <div className="grid gap-2">
                    {CATEGORIES.map((category) => (
                      <button
                        key={category.name}
                        onClick={() => {
                          navigateTo(categoryPath(category));
                          setShowCategories(false);
                        }}
                        className="flex items-center gap-3 rounded-xl p-2 text-left transition hover:bg-zinc-50"
                      >
                        <img src={category.image} alt={category.name} className="h-11 w-14 rounded-lg object-cover" />
                        <span className="text-sm font-medium text-slate-700">{category.name}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
          <button onClick={() => navigateTo("/tracked")} className={navClass("/tracked")}>
            Tracked Products
            <span className="ml-2 rounded-full bg-blue-100 px-2 py-0.5 text-xs text-radarBlue">{trackedProducts.length}</span>
          </button>
        </nav>
      </div>
    </header>
  );
}

function Toast() {
  const { toast, setToast } = useApp();
  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(null), 3000);
    return () => clearTimeout(timer);
  }, [toast, setToast]);
  if (!toast) return null;
  return (
    <div className={`mx-auto mt-5 w-full max-w-7xl rounded-2xl border px-5 py-3 text-sm ${toast.type === "error" ? "border-red-200 bg-red-50 text-red-700" : "border-emerald-200 bg-emerald-50 text-emerald-700"}`}>
      {toast.text}
    </div>
  );
}

function Hero() {
  const { trackProduct } = useApp();
  const [url, setUrl] = useState("");
  const [currentPrice, setCurrentPrice] = useState("");
  const [targetPrice, setTargetPrice] = useState("");

  const onQuickTrack = async () => {
    const cleanUrl = url.trim();
    if (!cleanUrl) {
      return;
    }
    let host = "External Store";
    try {
      host = new URL(cleanUrl).hostname.replace("www.", "");
    } catch (_error) {
      // URL validation handled in trackProduct
    }
    const quickProduct = {
      name: `Tracked Product (${host})`,
      store: host,
      product_url: cleanUrl,
      current_price: Number(currentPrice),
      category: "External",
      image: GENERIC_PRODUCT_PLACEHOLDER,
    };
    const ok = await trackProduct(quickProduct, targetPrice, cleanUrl);
    if (ok) {
      setUrl("");
      setCurrentPrice("");
      setTargetPrice("");
      navigateTo("/tracked");
    }
  };

  return (
    <section className="mx-auto mt-10 w-full max-w-[80rem] px-6">
      <article className="relative overflow-hidden rounded-[2rem] border border-zinc-200 shadow-[0_24px_80px_-45px_rgba(15,23,42,0.4)]">
        <img
          src={HERO_BACKGROUND_IMAGE}
          alt=""
          aria-hidden="true"
          className="absolute inset-0 h-full w-full object-cover object-center"
        />
        <div className="relative px-10 py-14">
          <div className="max-w-4xl">
          <h1 className="text-5xl font-semibold tracking-tight text-slate-900">
            You Set The Price.
            <br />
            We Track the Drops.
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-7 text-slate-600">
            We monitor electronics stores for you and alert when a product falls below your target.
          </p>
          <div className="mt-6 max-w-4xl grid gap-3 rounded-2xl border border-zinc-200 bg-zinc-50/90 p-4 md:grid-cols-[1.2fr_0.6fr_0.6fr_auto]">
            <input
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              type="url"
              placeholder="Paste external store product URL"
              className="rounded-xl border border-zinc-200 bg-white px-3 py-2 text-sm outline-none ring-radarBlue focus:ring-2"
            />
            <input
              value={currentPrice}
              onChange={(e) => setCurrentPrice(e.target.value)}
              type="number"
              min="0"
              step="0.01"
              placeholder="Current Price"
              className="rounded-xl border border-zinc-200 bg-white px-3 py-2 text-sm outline-none ring-radarBlue focus:ring-2"
            />
            <input
              value={targetPrice}
              onChange={(e) => setTargetPrice(e.target.value)}
              type="number"
              min="0"
              step="0.01"
              placeholder="Target Price"
              className="rounded-xl border border-zinc-200 bg-white px-3 py-2 text-sm outline-none ring-radarBlue focus:ring-2"
            />
            <button onClick={onQuickTrack} className="rounded-xl bg-radarBlue px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500">
              Track URL
            </button>
          </div>
          </div>
        </div>
      </article>
    </section>
  );
}

function ProductCard({ product }) {
  const { trackProduct } = useApp();
  const [target, setTarget] = useState("");
  const [storeUrl, setStoreUrl] = useState(product.product_url);

  const onTrack = async () => {
    const ok = await trackProduct(product, target, storeUrl);
    if (ok) navigateTo("/tracked");
  };

  return (
    <article className="group overflow-hidden rounded-3xl border border-zinc-200 bg-white shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-slate-200/80">
      <div className="flex h-48 items-center justify-center bg-white p-4">
        <img
          src={displayImageFor(product)}
          alt={product.name}
          onError={(event) => {
            event.currentTarget.src = fallbackImageFor(product);
          }}
          className="h-full w-full object-contain transition duration-500 group-hover:scale-105"
        />
      </div>
      <div className="p-5">
        <div className="mb-2 flex items-center justify-between">
          <span className="rounded-full bg-zinc-100 px-2.5 py-1 text-xs text-slate-600">{product.store}</span>
          <span className="text-sm font-semibold text-slate-900">{CURRENCY.format(product.current_price)}</span>
        </div>
        <h3 className="text-base font-semibold">{product.name}</h3>
        <p className="mt-1 text-xs text-slate-500">{product.category}</p>
        <div className="mt-4 space-y-2">
          <input value={storeUrl} onChange={(e) => setStoreUrl(e.target.value)} type="url" placeholder="Store product URL" className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-3 py-2 text-sm outline-none ring-radarBlue focus:ring-2" />
          <input value={target} onChange={(e) => setTarget(e.target.value)} type="number" min="0" step="0.01" placeholder="Your target price" className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-3 py-2 text-sm outline-none ring-radarBlue focus:ring-2" />
          <div className="flex gap-2">
            <button onClick={onTrack} className="flex-1 rounded-xl bg-radarBlue px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-500">Track Product</button>
            <button onClick={() => navigateTo(`/product/${product.id}`)} className="rounded-xl border border-zinc-200 px-3 py-2 text-sm text-slate-700 transition hover:border-radarBlue hover:text-radarBlue">Details</button>
          </div>
        </div>
      </div>
    </article>
  );
}

function HomePage() {
  const topDeals = useMemo(() => CATALOG.slice(0, 4), []);
  return (
    <>
      <Hero />
      <section className="mx-auto mt-10 w-full max-w-7xl px-6">
        <div className="mb-5 flex items-end justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">Top picks</p>
            <h2 className="text-3xl font-semibold tracking-tight">This week’s best electronics deals</h2>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {topDeals.map((product) => <ProductCard key={product.id} product={product} />)}
        </div>
      </section>
    </>
  );
}

function CategoryPage() {
  const route = useHashRoute();
  const slug = route.replace("#/category/", "");
  const category = findCategoryBySlug(slug);
  const products = category ? CATALOG.filter((product) => product.category === category.name) : [];

  if (!category) {
    navigateTo("/");
    return null;
  }

  return (
    <section className="mx-auto mt-10 w-full max-w-7xl px-6">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">Category</p>
          <h2 className="text-3xl font-semibold tracking-tight">{category.name}</h2>
        </div>
        <p className="text-sm text-slate-500">{products.length} products</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {products.map((product) => <ProductCard key={product.id} product={product} />)}
      </div>
    </section>
  );
}

function ProductDetailsPage() {
  const route = useHashRoute();
  const id = route.replace("#/product/", "");
  const product = CATALOG.find((p) => p.id === id);
  const { trackProduct } = useApp();
  const [target, setTarget] = useState(product ? String(Math.round(product.current_price * 0.9)) : "");
  const [storeUrl, setStoreUrl] = useState(product ? product.product_url : "");

  if (!product) {
    navigateTo("/");
    return null;
  }

  const onTrack = async () => {
    const ok = await trackProduct(product, target, storeUrl);
    if (ok) navigateTo("/tracked");
  };

  return (
    <section className="mx-auto mt-10 w-full max-w-7xl px-6">
      <button onClick={() => navigateTo(categoryPath(findCategoryBySlug(product.category.toLowerCase()) || { slug: "smartphones" }))} className="mb-4 rounded-full border border-zinc-200 bg-white px-4 py-2 text-sm">Back to {product.category}</button>
      <article className="grid overflow-hidden rounded-3xl border border-zinc-200 bg-white shadow-sm lg:grid-cols-2">
        <div className="flex min-h-[24rem] items-center justify-center bg-white p-8">
          <img
            src={displayImageFor(product)}
            alt={product.name}
            onError={(event) => {
              event.currentTarget.src = fallbackImageFor(product);
            }}
            className="h-full max-h-[28rem] w-full object-contain"
          />
        </div>
        <div className="p-8">
          <p className="text-sm text-slate-500">{product.category} • {product.store}</p>
          <h2 className="mt-2 text-3xl font-bold">{product.name}</h2>
          <p className="mt-3 text-2xl font-semibold text-radarBlue">{CURRENCY.format(product.current_price)}</p>
          <p className="mt-4 text-slate-600">Set your target, track this product, and get alerted when price goes below your threshold.</p>
          <div className="mt-6 space-y-3">
            <input value={storeUrl} onChange={(e) => setStoreUrl(e.target.value)} type="url" className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-3 py-2.5 text-sm outline-none ring-radarBlue focus:ring-2" placeholder="Store URL" />
            <input value={target} onChange={(e) => setTarget(e.target.value)} type="number" min="0" step="0.01" className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-3 py-2.5 text-sm outline-none ring-radarBlue focus:ring-2" />
            <button onClick={onTrack} className="rounded-xl bg-radarBlue px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-500">Track Product</button>
          </div>
        </div>
      </article>
    </section>
  );
}

function PriceChart({ data, target }) {
  const points = data;
  const values = points.map((p) => p.price).concat([target]);
  const min = Math.min(...values) * 0.97;
  const max = Math.max(...values) * 1.03;
  const chartWidth = 320;
  const chartHeight = 160;
  const plotLeft = 30;
  const plotRight = 290;
  const plotTop = 18;
  const plotBottom = 130;
  const xAt = (idx) => plotLeft + (idx * (plotRight - plotLeft)) / Math.max(points.length - 1, 1);
  const yAt = (val) => plotBottom - ((val - min) / Math.max(max - min, 1)) * (plotBottom - plotTop);
  const path = points.map((p, idx) => `${xAt(idx)},${yAt(p.price)}`).join(" ");
  const targetY = yAt(target);
  return (
    <div className="h-44 w-full rounded-2xl border border-zinc-200 bg-zinc-50 p-2">
      <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="h-full w-full">
        <rect x="0" y="0" width={chartWidth} height={chartHeight} fill="#f8fafc" />
        <line x1={plotLeft} y1={targetY} x2={plotRight} y2={targetY} stroke="#22c55e" strokeDasharray="4 4" strokeWidth="2" />
        <polyline points={path} fill="none" stroke="#3b82f6" strokeWidth="2.8" />
        {points.map((p, idx) => (
          <circle key={p.day} cx={xAt(idx)} cy={yAt(p.price)} r="2.8" fill="#2563eb" />
        ))}
        {points.map((p, idx) => (
          <text key={`${p.day}-lbl`} x={xAt(idx)} y="150" fontSize="9" textAnchor="middle" fill="#64748b">{p.day}</text>
        ))}
      </svg>
    </div>
  );
}

function TrackedPage() {
  const { trackedProducts, pauseTracked, resumeTracked, updateTrackedPricing, removeTracked, exportCsv } = useApp();
  const totalTracked = trackedProducts.length;
  const activeTracked = trackedProducts.filter((p) => p.is_active !== false).length;
  const avgTarget = totalTracked
    ? trackedProducts.reduce((sum, p) => sum + Number(p.target_price || 0), 0) / totalTracked
    : 0;
  return (
    <section className="mx-auto mt-10 w-full max-w-7xl px-6">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-3xl font-semibold tracking-tight">Tracked Products</h2>
        <button onClick={exportCsv} className="rounded-full border border-zinc-200 bg-white px-4 py-2 text-sm text-slate-700">Export CSV</button>
      </div>
      <div className="mb-5 grid gap-3 sm:grid-cols-3">
        <div className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm">
          <p className="text-xs text-slate-500">Total Tracked</p>
          <p className="mt-1 text-2xl font-semibold">{totalTracked}</p>
        </div>
        <div className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm">
          <p className="text-xs text-slate-500">Active Items</p>
          <p className="mt-1 text-2xl font-semibold">{activeTracked}</p>
        </div>
        <div className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm">
          <p className="text-xs text-slate-500">Avg Target Price</p>
          <p className="mt-1 text-2xl font-semibold">{CURRENCY.format(avgTarget)}</p>
        </div>
      </div>
      {!trackedProducts.length ? (
        <div className="rounded-3xl border border-zinc-200 bg-white p-10 text-center text-slate-500 shadow-sm">
          No tracked products yet. Open a category and click `Track Product`.
        </div>
      ) : (
        <div className="grid gap-5 lg:grid-cols-2">
          {trackedProducts.map((product) => {
            const diff = product.current_price - product.target_price;
            return (
              <TrackedProductCard
                key={product.id}
                product={product}
                diff={diff}
                onPause={pauseTracked}
                onResume={resumeTracked}
                onSavePricing={updateTrackedPricing}
                onDelete={removeTracked}
              />
            );
          })}
        </div>
      )}
    </section>
  );
}

function TrackedProductCard({ product, diff, onPause, onResume, onSavePricing, onDelete }) {
  const [currentPriceInput, setCurrentPriceInput] = useState(String(product.current_price));
  const [targetPriceInput, setTargetPriceInput] = useState(String(product.target_price));

  useEffect(() => {
    setCurrentPriceInput(String(product.current_price));
    setTargetPriceInput(String(product.target_price));
  }, [product.current_price, product.target_price]);

  const handleSave = async () => {
    await onSavePricing(product.id, currentPriceInput, targetPriceInput);
  };

  return (
    <article className="rounded-3xl border border-zinc-200 bg-white p-5 shadow-sm">
      <div className="mb-3 flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white p-2 ring-1 ring-zinc-200">
            <img
              src={displayImageFor(product)}
              alt={product.name}
              onError={(event) => {
                event.currentTarget.src = fallbackImageFor(product);
              }}
              className="h-full w-full object-contain"
            />
          </div>
          <div>
            <h3 className="font-semibold">{product.name}</h3>
            <p className="text-xs text-slate-500">{product.store} · {product.category}</p>
          </div>
        </div>
        <span className={`rounded-full px-2.5 py-1 text-xs ${product.status === "price-dropped" ? "bg-emerald-50 text-emerald-600" : product.status === "paused" ? "bg-zinc-100 text-slate-600" : "bg-blue-50 text-radarBlue"}`}>
          {product.status === "price-dropped" ? "Price Dropped" : product.status === "paused" ? "Paused" : "Tracking"}
        </span>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-3 text-sm">
        <div className="rounded-xl bg-zinc-50 p-3"><p className="text-slate-500">Current</p><p className="font-semibold">{CURRENCY.format(product.current_price)}</p></div>
        <div className="rounded-xl bg-zinc-50 p-3"><p className="text-slate-500">Target</p><p className="font-semibold text-radarBlue">{CURRENCY.format(product.target_price)}</p></div>
        <div className="rounded-xl bg-zinc-50 p-3"><p className="text-slate-500">Difference</p><p className={`font-semibold ${diff <= 0 ? "text-emerald-600" : "text-amber-600"}`}>{CURRENCY.format(Math.abs(diff))}</p></div>
      </div>
      <div className="mb-4 grid gap-3 rounded-2xl border border-zinc-200 bg-zinc-50 p-3 md:grid-cols-[1fr_1fr_auto]">
        <input
          value={currentPriceInput}
          onChange={(e) => setCurrentPriceInput(e.target.value)}
          type="number"
          min="0"
          step="0.01"
          placeholder="Current Price"
          className="rounded-xl border border-zinc-200 bg-white px-3 py-2 text-sm outline-none ring-radarBlue focus:ring-2"
        />
        <input
          value={targetPriceInput}
          onChange={(e) => setTargetPriceInput(e.target.value)}
          type="number"
          min="0"
          step="0.01"
          placeholder="Target Price"
          className="rounded-xl border border-zinc-200 bg-white px-3 py-2 text-sm outline-none ring-radarBlue focus:ring-2"
        />
        <button onClick={handleSave} className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700">
          Update Prices
        </button>
      </div>
      <PriceChart data={product.history} target={product.target_price} />
      <div className="mt-3 flex gap-2">
        {product.is_active !== false ? (
          <button onClick={() => onPause(product.id)} className="rounded-lg border border-zinc-200 px-3 py-1.5 text-xs text-slate-700">Pause</button>
        ) : (
          <button onClick={() => onResume(product.id)} className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs text-emerald-700">Resume</button>
        )}
        <button onClick={() => onDelete(product.id)} className="rounded-lg border border-red-200 px-3 py-1.5 text-xs text-red-600">Delete</button>
      </div>
    </article>
  );
}

function Footer() {
  return (
    <footer className="mx-auto mt-16 w-full max-w-7xl px-6 pb-8">
      <div className="rounded-[2rem] border border-zinc-200 bg-white px-6 py-5 text-sm text-slate-500 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p>© {new Date().getFullYear()} PriceRadar. Premium Price Tracking.</p>
          <a href="/alerts/email-preview" target="_blank" className="hover:text-radarBlue">Email alert preview</a>
        </div>
      </div>
    </footer>
  );
}

function AppShell() {
  const route = useHashRoute();
  useEffect(() => {
    const id = setTimeout(() => lucide.createIcons(), 0);
    return () => clearTimeout(id);
  });
  let page = <HomePage />;
  if (route.startsWith("#/category/")) page = <CategoryPage />;
  if (route === "#/tracked") page = <TrackedPage />;
  if (route.startsWith("#/product/")) page = <ProductDetailsPage />;
  return (
    <div className="pb-12">
      <TopNav />
      <Toast />
      {page}
      <Footer />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <AppProvider>
    <AppShell />
  </AppProvider>
);
