import streamlit as st
import airtable
import os

menu = {
        'Nourriture': {
            'Pizza (10€)': 10.00,
            'Burger': 8.00,
            'Sandwich': 6.00,
            'Salade': 7.00,
        },
        'Boisson': {
            'Soda': 2.00,
            'Jus': 3.00,
            'Café': 4.00,
            'Thé': 3.50,
        },
        'Mystère': {
            'Lot mystère A': 15.00,
            'Lot mystère B': 20.00,
        },
    }

def add_to_airtable(name, num_person, order):
    base_key = os.environ.get('AIRTABLE_BASE_KEY')
    api_key = os.environ.get('AIRTABLE_API_KEY')
    base = airtable.Airtable(base_key, 'Orders', api_key)

    items = []
    total = 0

    for category, items_dict in order.items():
        for item, qty in items_dict.items():
            if qty > 0:
                item_str = f'{qty} x {item} ({menu[category][item] * qty} €)'
                items.append(item_str)
                total += menu[category][item] * qty

    record = {
        'Nom': name,
        'Nombre de Personne': num_person,
        'Items': ', '.join(items),
        'Total': total
    }

    base.insert(record)

def restaurant_ordering_system():
    st.set_page_config(page_title="📎 Soirée Collecte de Fond")
    st.title('📎 Soirée Collecte de Fond')
    st.markdown("---")

    if 'page' not in st.session_state:
        st.session_state.page = 0

    if 'order' not in st.session_state:
        st.session_state.order = {'Nourriture': {}, 'Boisson': {}, 'Mystère': {}}

    if 'name' not in st.session_state:
        st.session_state.name = None

    if 'num_person' not in st.session_state:
        st.session_state.num_person = None

    if st.session_state.page == 0:
        st.write('# 📍 **Information:**')
        st.session_state.name = st.text_input('✏️ Nom')
        st.session_state.num_person = st.number_input('✏️ Nombre de personnes', min_value=1, max_value=10, value=1)
        
        disabled = not st.session_state.name or st.session_state.num_person < 1

        if st.button('Suivant ➡️', key='next1', disabled=disabled):
            st.session_state.page += 1
            st.rerun()

    elif st.session_state.page == 1:
        st.write('# 🏷️ **Menu:**')
        st.write('Merci de choisir votre **commande** puis de choisir la **quantité**.')

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("---")
            st.markdown('### 😋 Nourriture')
            food_order = st.multiselect('Sélectionner la nourriture:', list(menu['Nourriture'].keys()), key='food_select')
            st.session_state.order['Nourriture'] = {item: st.number_input(f'Quantité pour {item}:', min_value=1, max_value=10, value=1, key=f'food_{item}') for item in food_order}

        with col2:
            st.markdown("---")
            st.markdown('### 🥤 Boissons')
            drink_order = st.multiselect('Sélectionner les boissons:', list(menu['Boisson'].keys()), key='drink_select')
            st.session_state.order['Boisson'] = {item: st.number_input(f'Quantité pour {item}:', min_value=1, max_value=10, value=1, key=f'drink_{item}') for item in drink_order}

        with col3:
            st.markdown("---")
            st.markdown('### 👁️‍🗨️ Lots mystères')
            mystery_order = st.multiselect('Sélectionner les lots mystères:', list(menu['Mystère'].keys()), key='mystery_select')
            st.session_state.order['Mystère'] = {item: st.number_input(f'Quantité pour {item}:', min_value=1, max_value=10, value=1, key=f'mystery_{item}') for item in mystery_order}

        # Désactiver le bouton si moins d'un élément est sélectionné
        disabled = sum(st.session_state.order['Nourriture'].values()) < 1 and sum(st.session_state.order['Boisson'].values()) < 1 and sum(st.session_state.order['Mystère'].values()) < 1

        if st.button('Suivant ➡️', key='next2', disabled=disabled):
            st.session_state.page += 1
            st.rerun()
        if st.button('⬅️ Précédent', key='prev2'):
            st.session_state.page -= 1
            st.rerun()

    elif st.session_state.page == 2:
        total = 0.0
        st.write('# 🧺 **Récapitulatif de la commande:**')
        st.write('Vérifier votre **commande** et la **quantité** de chaque.')
        for category, items in st.session_state.order.items():
            if items:
                for item, qty in items.items():
                    if qty > 0:  # Affiche seulement si la quantité est supérieure à 0
                        price = menu[category][item] * qty
                        st.write(f'- {qty} x {item}: {price} €')
                        total += price
        st.metric('🧮 Total de la commande', f'{total} €')

        if st.button('💵 Passer la commande'):
            add_to_airtable(st.session_state.name, st.session_state.num_person, st.session_state.order)
            st.success(f'✅ Merci {st.session_state.name} pour votre commande! Vous pouvez fermer cet onglet.')

        if st.button('⬅️ Précédent', key='prev3'):
            st.session_state.page -= 1
            st.rerun()

if __name__ == '__main__':
    restaurant_ordering_system()
