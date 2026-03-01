import streamlit as st
import json
from datetime import datetime
import re

st.set_page_config(page_title="AgentAir Schema Fixer", layout="centered")

st.title("🛠️ AgentAir Schema Fixer")
st.markdown("Generate proper schema markup so AI can understand your business.")

# Business type mapping
BUSINESS_TYPES = {
    "Plumber": "Plumber",
    "Electrician": "Electrician",
    "Roofer": "RoofingContractor",
    "HVAC": "HVACBusiness",
    "Contractor": "GeneralContractor",
    "Landscaper": "Landscaping",
    "Painter": "Painting",
    "Dentist": "Dentist",
    "Lawyer": "LegalService",
    "Restaurant": "Restaurant",
    "General": "LocalBusiness"
}

with st.form("schema_form"):
    st.subheader("📋 Business Information")
    
    col1, col2 = st.columns(2)
    with col1:
        business_name = st.text_input("Business Name *", placeholder="Joe's Plumbing")
        business_type = st.selectbox("Business Type *", options=list(BUSINESS_TYPES.keys()))
        phone = st.text_input("Phone *", placeholder="(408) 555-0123")
    
    with col2:
        website = st.text_input("Website *", placeholder="https://example.com")
        email = st.text_input("Email (optional)", placeholder="info@example.com")
        price_range = st.select_slider("Price Range", options=["$", "$$", "$$$", "$$$$"], value="$$")
    
    st.subheader("📍 Address")
    col3, col4 = st.columns(2)
    with col3:
        street = st.text_input("Street Address *", placeholder="123 Main St")
        city = st.text_input("City *", placeholder="San Jose")
    with col4:
        state = st.text_input("State *", max_chars=2, placeholder="CA")
        zip_code = st.text_input("ZIP *", placeholder="95112")
    
    st.subheader("⏰ Hours of Operation")
    st.caption("Leave blank if not open that day")
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    hours = {}
    
    for day in days:
        col_time1, col_time2 = st.columns(2)
        with col_time1:
            open_time = st.time_input(f"{day} Open", value=None, key=f"{day}_open", label_visibility="collapsed")
        with col_time2:
            close_time = st.time_input(f"{day} Close", value=None, key=f"{day}_close", label_visibility="collapsed")
        
        if open_time and close_time:
            hours[day.lower()] = {
                "open": open_time.strftime("%H:%M"),
                "close": close_time.strftime("%H:%M")
            }
    
    submitted = st.form_submit_button("🚀 Generate Schema", type="primary")

def clean_phone(phone):
    """Remove non-numeric characters from phone."""
    return re.sub(r'\D', '', phone)

def generate_schema(data):
    """Generate JSON-LD schema from form data."""
    
    schema_type = BUSINESS_TYPES[data['business_type']]
    
    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": data['business_name'],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": data['street'],
            "addressLocality": data['city'],
            "addressRegion": data['state'].upper(),
            "postalCode": data['zip'],
            "addressCountry": "US"
        },
        "telephone": clean_phone(data['phone']),
        "url": data['website'],
        "priceRange": data['price_range']
    }
    
    # Add optional email
    if data.get('email'):
        schema["email"] = data['email']
    
    # Add hours if any
    if data.get('hours'):
        day_map = {
            'monday': 'Monday', 'tuesday': 'Tuesday', 'wednesday': 'Wednesday',
            'thursday': 'Thursday', 'friday': 'Friday', 'saturday': 'Saturday', 'sunday': 'Sunday'
        }
        
        hours_spec = []
        for day, times in data['hours'].items():
            if times.get('open') and times.get('close'):
                hours_spec.append({
                    "@type": "OpeningHoursSpecification",
                    "dayOfWeek": day_map.get(day, day),
                    "opens": times['open'],
                    "closes": times['close']
                })
        
        if hours_spec:
            schema["openingHoursSpecification"] = hours_spec
    
    return json.dumps(schema, indent=2)

if submitted:
    # Validate required fields
    required = {
        "Business Name": business_name,
        "Street Address": street,
        "City": city,
        "State": state,
        "ZIP": zip_code,
        "Phone": phone,
        "Website": website
    }
    
    missing = [field for field, value in required.items() if not value]
    
    if missing:
        st.error(f"Missing required fields: {', '.join(missing)}")
    else:
        # Build data dict
        data = {
            'business_name': business_name,
            'business_type': business_type,
            'street': street,
            'city': city,
            'state': state,
            'zip': zip_code,
            'phone': phone,
            'website': website,
            'email': email,
            'price_range': price_range,
            'hours': hours
        }
        
        # Generate schema
        schema_json = generate_schema(data)
        
        # Format as HTML with script tags
        html_output = f'''<!-- Schema generated by AgentAir -->
<script type="application/ld+json">
{schema_json}
</script>'''
        
        st.success("✅ Schema generated successfully!")
        
        st.subheader("📋 Copy this code")
        st.code(html_output, language="html")
        
        st.info(
            "Paste this code into the `<head>` section of your website, "
            "or use a WordPress plugin like 'Insert Headers and Footers'."
        )
        
        # Download options
        col_json, col_html = st.columns(2)
        
        with col_json:
            st.download_button(
                "📥 Download JSON",
                schema_json,
                file_name=f"{business_name.lower().replace(' ', '_')}_schema.json",
                mime="application/json"
            )
        
        with col_html:
            st.download_button(
                "📥 Download HTML",
                html_output,
                file_name=f"{business_name.lower().replace(' ', '_')}_schema.html",
                mime="text/html"
            )
        
        # Validation link
        st.markdown("""
        ### ✅ Next Steps
        1. Copy the code above
        2. Paste into your website's `<head>` section
        3. Test it with Google's [Rich Results Test](https://search.google.com/test/rich-results)
        """)
