// Mock data for The Atelier frontend (replaces live API calls)

export const CATEGORIES = [
  { id: 1, category: 'Clothing' },
  { id: 2, category: 'Accessories' },
  { id: 3, category: 'Footwear' },
  { id: 4, category: 'Bags' },
  { id: 5, category: 'Jewellery' },
]

export const PRODUCTS = [
  {
    p_id: 1,
    product_name: 'Obsidian Wool Overcoat',
    brand: 'Maison Noir',
    price: 1290.00,
    category: 1,
    category_name: 'Clothing',
    description: 'A statement piece crafted from the finest Italian wool. Tailored for the discerning individual with a structured silhouette and minimalist detailing.',
    image: 'https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=600&q=80',
    stock: 8,
  },
  {
    p_id: 2,
    product_name: 'Cairo Leather Tote',
    brand: 'Atelier Nord',
    price: 645.00,
    category: 4,
    category_name: 'Bags',
    description: 'Hand-stitched full-grain leather tote. Spacious interior with suede lining, brass hardware, and a removable zip pouch.',
    image: 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&q=80',
    stock: 14,
  },
  {
    p_id: 3,
    product_name: 'Venetian Silk Scarf',
    brand: 'Casa Seta',
    price: 320.00,
    category: 2,
    category_name: 'Accessories',
    description: 'Pure mulberry silk scarf with a hand-rolled hem. Featuring an exclusive artisan print inspired by Venetian mosaics.',
    image: 'https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=600&q=80',
    stock: 22,
  },
  {
    p_id: 4,
    product_name: 'Nocturne Derby Shoe',
    brand: 'Cordwainer & Co.',
    price: 890.00,
    category: 3,
    category_name: 'Footwear',
    description: 'Blake-stitched calf leather derby with a burnished toe cap. A timeless silhouette refined for the modern wardrobe.',
    image: 'https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=600&q=80',
    stock: 5,
  },
  {
    p_id: 5,
    product_name: 'Aurelius Gold Cufflinks',
    brand: 'Maison Gilt',
    price: 425.00,
    category: 5,
    category_name: 'Jewellery',
    description: 'Solid 18k gold cufflinks with a double-sided toggle. Each pair arrives in a hand-crafted lacquered box.',
    image: 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=600&q=80',
    stock: 3,
  },
  {
    p_id: 6,
    product_name: 'Alabaster Cashmere Knit',
    brand: 'Maison Noir',
    price: 580.00,
    category: 1,
    category_name: 'Clothing',
    description: 'Two-ply grade-A cashmere crew neck in a soft ivory palette. An investment piece that only gets better with time.',
    image: 'https://images.unsplash.com/photo-1575032617751-6ddec2089882?w=600&q=80',
    stock: 11,
  },
  {
    p_id: 7,
    product_name: 'Rivière Ceramic Watch',
    brand: 'Horlogerie Suisse',
    price: 2150.00,
    category: 2,
    category_name: 'Accessories',
    description: 'Swiss quartz movement encased in a matte white ceramic case. A clean, minimal dial that speaks quietly of confidence.',
    image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80',
    stock: 2,
  },
  {
    p_id: 8,
    product_name: 'Dusk Suede Chelsea Boot',
    brand: 'Cordwainer & Co.',
    price: 750.00,
    category: 3,
    category_name: 'Footwear',
    description: 'Supple sand suede Chelsea boot with elastic gussets and a hand-welted sole. Built to be worn every day for a decade.',
    image: 'https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=600&q=80',
    stock: 0,
  },
]

export const MOCK_ORDERS = [
  {
    o_id: 1001,
    order_date: '2026-03-10',
    status: 'PAID',
    total_amount: 1935.00,
    items: [
      { p_id: 3, product_name: 'Venetian Silk Scarf', quantity: 1, price_at_purchase: 320.00 },
      { p_id: 4, product_name: 'Nocturne Derby Shoe', quantity: 1, price_at_purchase: 890.00 },
      { p_id: 6, product_name: 'Alabaster Cashmere Knit', quantity: 1, price_at_purchase: 725.00 },
    ],
  },
  {
    o_id: 1002,
    order_date: '2026-03-22',
    status: 'CREATED',
    total_amount: 645.00,
    items: [
      { p_id: 2, product_name: 'Cairo Leather Tote', quantity: 1, price_at_purchase: 645.00 },
    ],
  },
]

export const MOCK_BANK_ACCOUNTS = [
  { acc_no: 4001, bank_name: 'Creston Private Bank', expiry_date: '2028-06-30' },
  { acc_no: 4002, bank_name: 'Meridian Trust',       expiry_date: '2027-12-31' },
]
