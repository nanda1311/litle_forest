# Little Forest
https://litleforest.com/

Little Forest is an online marketplace for bonsai trees and terrariums, serving customers looking to buy bonsai plants in Bangalore and beyond. The platform lets customers browse curated plant collections, view detailed product information, and purchase online, with guidance provided at every step of plant ownership.

---

## Overview

Little Forest operates as a standard e-commerce storefront built around a single product category: bonsai and terrarium plants. The platform combines product browsing, account management, and content (blog, FAQ, policies) to support customers before and after purchase.

The site serves one primary type of user:

- **Customers**, who browse the catalog, manage a cart and wishlist, create an account, and place orders.

An underlying admin/catalog management layer (not customer-facing) maintains product listings, categories, pricing, and blog content.

---

## How the Platform Works

### 1. Browsing and Discovery

1. A visitor lands on the homepage, which highlights featured categories (Ficus, Fructiflorous, Sculptural, Jade Bonsai, Terrarium) and newly added products.
2. From the homepage or the navigation menu, the visitor can go to the Store/Collection page to view the full catalog, or to the dedicated Terrarium page for that category.
3. Each product is listed with an image, name, category, price (with any discount shown against the original price), height, and approximate age.

### 2. Product Selection

1. Clicking a product opens its dedicated product page with full details.
2. From either the catalog listing or the product page, the customer can:
   - Add the item to the **Cart** for purchase.
   - Add the item to the **Wishlist** to save it for later.

### 3. Account and Checkout

1. New customers can register for an account; returning customers log in.
2. Cart and wishlist contents are tied to the customer's account, allowing items to be saved across sessions.
3. From the Cart page, the customer proceeds through checkout to complete an order.
4. Order-related policies (refunds, terms, and delivery expectations) are available through the footer links at any point in this process.

### 4. Post-Purchase Support

1. Little Forest provides plant care guidance after purchase, along with a stated health guarantee period on delivered plants.
2. Customers with questions can reach the team directly through the Contact page or the WhatsApp chat link available site-wide.
3. The FAQ page addresses common questions without requiring direct contact.

### 5. Content and Trust Building

1. The Blog section publishes articles on bonsai care, gifting, and beginner guidance, helping customers make informed decisions and supporting organic discovery of the site.
2. Customer testimonials are featured on the homepage to build trust with new visitors.
3. Policy pages (Privacy Policy, Terms of Service, Refund Policy) are linked from the footer for transparency.

---

## Core Features

- Product catalog organized by category, with dedicated collection pages.
- Individual product pages with pricing, dimensions, and age details.
- Cart and wishlist functionality tied to customer accounts.
- Customer account system with login and registration.
- Blog for care guides and plant-related content.
- Customer testimonials displayed on the homepage.
- FAQ, Privacy Policy, Terms of Service, and Refund Policy pages.
- Direct contact via a contact page and WhatsApp integration.
- Responsive design for both desktop and mobile browsing.

---

## Technology Stack

The site is server-rendered with a template-based architecture (consistent with a Python/Django backend, based on the site's structure and CSRF token usage), paired with standard front-end technologies.

| Layer | Technology |
|---|---|
| Backend | Python, Django (inferred from site structure) |
| Frontend | HTML, CSS, JavaScript |
| Media | Product and blog images served from a dedicated media directory |
---
