import streamlit as st
import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://lyanh10x:GNyyas1EK6ACut8M@cluster0.8pd05.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

database = client["Northwind"]
collection = database["products"]

products_to_order = collection.find({
    "$expr": {
        "$gt": [
            {"$toInt": "$ReorderLevel"}, 
            {"$add": [
                {"$toInt": "$UnitsInStock"}, 
                {"$toInt": "$UnitsOnOrder"}
            ]}
        ]
    }
})

st.title("Produkter som behöver beställas")

products = []

for product in products_to_order:
    product_id = product["_id"]
    product_name = product["ProductName"]
    units_in_stock = product["UnitsInStock"]
    units_on_order = product["UnitsOnOrder"]
    reorder_level = product["ReorderLevel"]
    
    supplier = product.get("supplier_info", {})
    supplier_id = supplier.get("SupplierID", "Okänd SupplierID")
    contact_name = supplier.get("ContactName", "Okänd kontakt")
    phone = supplier.get("Phone", "Okänt telefonnummer")
    
    products.append({
        "ProduktID": product_id,
        "Produktnamn": product_name,
        "Units In Stock": units_in_stock,
        "Units On Order": units_on_order,
        "Reorder Level": reorder_level,
        "SupplierID": supplier_id,
        "Kontaktperson": contact_name,
        "Telefon": phone
    })

if products:
    df = pd.DataFrame(products)
    st.table(df)
else:
    st.write("Inga produkter behöver beställas för tillfället.")
    

import streamlit as st
import qrcode
from pymongo import MongoClient
from PIL import Image
import io


uri = "mongodb+srv://lyanh10x:GNyyas1EK6ACut8M@cluster0.8pd05.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
database = client["Northwind"]
collection = database["products"]

products_to_order = collection.find({
    "$expr": {
        "$gt": ["$ReorderLevel", {"$add": ["$UnitsInStock", "$UnitsOnOrder"]}]
    }
})

for product in products_to_order:
    product_id = product["_id"]
    product_name = product["ProductName"]
    units_in_stock = product["UnitsInStock"]
    units_on_order = product["UnitsOnOrder"]
    reorder_level = product["ReorderLevel"]
    
    supplier = product.get("supplier_info", {})  
    supplier_id = supplier.get("SupplierID", "Okänd SupplierID")
    contact_name = supplier.get("ContactName", "Okänd kontakt")
    phone = supplier.get("Phone", "Okänt telefonnummer")
    
    qr_data = f"ProduktID: {product_id}\nProduktnamn: {product_name}\nUnits In Stock: {units_in_stock}\nUnits On Order: {units_on_order}\nReorder Level: {reorder_level}\nSupplierID: {supplier_id}\nKontaktperson: {contact_name}\nTelefon: {phone}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    st.write(f"### Produkt: {product_name}")
    st.write(f" Produkt ID: {product_id}")
    st.write(f" Kontaktperson: {contact_name}")
    st.write(f" Telefon: {phone}")
    
    buf = io.BytesIO()  
    img.save(buf)
    buf.seek(0)  
    st.image(buf, caption=f"QR-kod för att beställa {product_name}", use_column_width=True)
    st.write("-" * 40)
