import streamlit as st
import time
from frontend.utils import api_request, show_error, show_success, format_datetime

def show_admin_documents():
    st.title("📁 Gestión Documental")
    
    # --- Top Actions (Reindex) ---
    col1, col2 = st.columns([4, 2])
    with col2:
        if st.button("🔄 Reindexar Base de Datos", use_container_width=True, type="primary"):
            with st.spinner("Reindexando documentos... esto puede tomar tiempo."):
                success, response = api_request("POST", "/admin/documents/reindex")
                if success:
                    st.toast("¡Reindexado completo!", icon="✅")
                    st.success(f"Procesado en {response.get('time_seconds')}s. Chunks: {response.get('chunks_indexed')}")
                    time.sleep(2)
                    st.rerun()
                else:
                    show_error(f"Error al reindexar: {response}")

    st.markdown("---")
    
    # --- Upload Area ---
    st.subheader("📤 Subir Documentos")
    uploaded_files = st.file_uploader(
        "Arrastra archivos PDF, DOCX, TXT o MD aquí", 
        accept_multiple_files=True,
        type=["pdf", "docx", "txt", "md"]
    )
    
    if uploaded_files:
        if st.button(f"Subir {len(uploaded_files)} archivos"):
            with st.spinner("Subiendo archivos..."):
                # Prepare files for requests
                # requests expects files as list of tuples: ('files', (filename, file_obj, content_type))
                files_payload = []
                for f in uploaded_files:
                    files_payload.append(
                       ("files", (f.name, f.getvalue(), f.type))
                    )
                
                success, response = api_request("POST", "/admin/documents/upload", files=files_payload)
                
                if success:
                    st.success(f"Se subieron {response.get('uploaded')} archivos correctamente.")
                    st.info("Recuerda pulsar 'Reindexar' para que el sistema aprenda el nuevo contenido.")
                    time.sleep(2)
                    st.rerun()
                else:
                    show_error(f"Error al subir: {response}")

    st.markdown("---")
    
    # --- Document List ---
    st.subheader("📚 Documentos en Biblioteca")
    
    success, docs = api_request("GET", "/admin/documents")
    
    if success and docs:
        # Table Header
        h1, h2, h3, h4 = st.columns([3, 1, 2, 1])
        h1.markdown("**Archivo**")
        h2.markdown("**Tamaño**")
        h3.markdown("**Modificado**")
        h4.markdown("**Acción**")
        st.divider()
        
        for doc in docs:
            c1, c2, c3, c4 = st.columns([3, 1, 2, 1])
            with c1:
                icon = "📄"
                if doc['extension'] == ".pdf": icon = "📕"
                elif doc['extension'] == ".docx": icon = "📘"
                
                st.write(f"{icon} {doc['filename']}")
            
            with c2:
                # Format size
                size_kb = doc['size_bytes'] / 1024
                st.text(f"{size_kb:.1f} KB")
            
            with c3:
                st.text(format_datetime(doc['modified']))
            
            with c4:
                if st.button("🗑️", key=f"del_{doc['filename']}", help="Eliminar archivo"):
                     show_delete_doc_dialog(doc)
            
            st.markdown("---")
            
    else:
        st.info("No hay documentos en la biblioteca o no se pudieron cargar.")

@st.dialog("Eliminar Documento")
def show_delete_doc_dialog(doc):
    st.warning(f"¿Estás seguro que deseas eliminar **{doc['filename']}**?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("Sí, Eliminar", type="primary", use_container_width=True):
             success, response = api_request("DELETE", f"/admin/documents/{doc['filename']}")
             if success:
                 st.success("Archivo eliminado.")
                 st.info("Se recomienda reindexar para actualizar la base de conocimientos.")
                 time.sleep(2)
                 st.rerun()
             else:
                 show_error(f"Error: {response}")

# Alias
admin_documents_page = show_admin_documents
