import React from 'react';
// Demonstrates the error: Module not found: Can't resolve './ProductCard'
import ProductCard from './ProductCard';

export const ProductCatalog = () => {
  return (
    <div className="product-catalog">
      <h2>Active Product Catalog</h2>
      <ProductCard />
    </div>
  );
};

export default ProductCatalog;
