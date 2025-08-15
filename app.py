import streamlit as st
import streamlit.runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx
from tornado import httputil

# --- The Core Function ---
def get_cookie_from_headers(cookie_name: str) -> str | None:
    """
    A workaround to read a cookie (including HttpOnly) from the initial request headers.
    This is compatible with the Streamlit runtime structure.
    
    Args:
        cookie_name (str): The name of the cookie to retrieve.

    Returns:
        str | None: The cookie value if found, otherwise None.
    """
    try:
        ctx = get_script_run_ctx()
        if ctx is None:
            return None

        session_id = ctx.session_id
        runtime = streamlit.runtime.get_instance()
        session_info = runtime._session_mgr.get_session_info(session_id)

        if session_info is None:
            return None

        headers = session_info.client.request.headers
        cookie_string = headers.get('Cookie')

        if not cookie_string:
            return None

        cookies = httputil.parse_cookie(cookie_string)
        return cookies.get(cookie_name)

    except Exception:
        return None

# --- Example App ---
st.set_page_config(
    page_title="HttpOnly Cookie Tester",
    layout='centered'
)

st.title("🧪 Streamlit HttpOnly Cookie Tester")

# --- User Input ---
cookie_to_find = st.text_input(
    "Enter the name of the HttpOnly cookie you want to find:",
    "YOUR_COOKIE_HTTP_ONLY"
)

# --- Attempt to Read the Cookie ---
if st.button("Find Cookie", type="primary"):
    st.header("Results")
    with st.spinner(f"Searching for cookie '{cookie_to_find}'..."):
        cookie_value = get_cookie_from_headers(cookie_name=cookie_to_find)

        if cookie_value:
            st.success(f"🎉 Success! Found the cookie.")
            st.code(cookie_value, language=None)
        else:
            st.error(f"❌ Failure! Could not find the cookie named '{cookie_to_find}'.")
            st.info("Please check the following:")
            st.markdown("""
                - Is the cookie name spelled correctly?
                - Is the cookie present in your browser for this domain?
            """)
