# Streamlit HttpOnly Cookie Getter

A simple and effective workaround to read `HttpOnly` cookies in a Streamlit application. This repository provides a function and a test application to solve a common challenge where JavaScript-based solutions fail.

[![made-in-Brazil](https://img.shields.io/badge/made%20in-Brazil-009B3A.svg?style=flat-square)](https://www.google.com/search?q=Brazil)

---

## Motivation

The development of this solution was driven by a real-world need: integrating a Streamlit application into a Kubernetes environment behind an authentication gateway. The gateway would validate the user and set an `HttpOnly` session cookie. To avoid forcing users to log in twice, the Streamlit app needed to read this cookie to get the user's identity. This "hack" was developed to bridge that gap.

## The Problem

Accessing `HttpOnly` cookies in Streamlit is challenging because:

- **No Native Support:** Streamlit does not provide a built-in function to read `HttpOnly` cookies.
- **Security Restrictions:** These cookies are protected from client-side scripts (JavaScript) to prevent XSS attacks, meaning standard browser-based libraries cannot access them.
- **Integration Issues:** This becomes a problem when integrating a Streamlit app with authentication systems that rely on `HttpOnly` cookies for session management.

## The Solution

This repository provides a Python-based workaround that directly accesses the initial HTTP request headers received by the Streamlit server.

- It operates on the **server-side context** of the Streamlit application.
- It inspects the raw `Cookie` header from the user's connection request.
- By parsing this header, it can extract any cookie's value, bypassing the browser's client-side security restrictions.

## Usage

To use this solution in your own Streamlit project, simply copy the `get_cookie_from_headers` function into your code.

### The Function

```python
import streamlit.runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx
from tornado import httputil

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
        # Get the script run context to access session information
        ctx = get_script_run_ctx()
        if ctx is None:
            return None

        # Get session details
        session_id = ctx.session_id
        runtime = streamlit.runtime.get_instance()
        session_info = runtime._session_mgr.get_session_info(session_id)

        if session_info is None:
            return None

        # Access headers from the session info's client request
        headers = session_info.client.request.headers
        cookie_string = headers.get('Cookie')

        if not cookie_string:
            return None

        # Parse the cookie string to a dictionary
        cookies = httputil.parse_cookie(cookie_string)
      
        # Return the specific cookie value
        return cookies.get(cookie_name)

    except Exception:
        # If any part of the hack fails (e.g., due to future Streamlit updates),
        # return None to prevent the app from crashing.
        return None
```

### Example

Here is how you can use it in your app to retrieve an authentication token:

```python
import streamlit as st

# Assume get_cookie_from_headers is defined in this file or imported
auth_token = get_cookie_from_headers(cookie_name="YOUR_AUTH_COOKIE")

if auth_token:
    st.success(f"Welcome! Your auth token is: {auth_token}")
    # Proceed with authenticated logic
else:
    st.error("Authentication cookie not found. Please log in.")
    # Redirect to login page or show an error
```

## Testing with the Example App

This repository includes `app.py`, a simple Streamlit application to test the function and verify that it can read `HttpOnly` cookies in your environment.

### How to Run the Test App

1. **Clone the repository:**

   ```bash
   git clone git@github.com:omatheusgit/streamlit-httponly-cookies.git
   cd streamlit-httponly-cookies
   ```
2. **Install dependencies:**

   ```bash
   pip install streamlit
   ```
3. **Run the app:**

   ```bash
   streamlit run app.py
   ```
4. **Test in your browser:**

   * Open the app in your browser.
   * Use your browser's developer tools or a backend service to set an `HttpOnly` cookie for the app's domain (e.g., `localhost`).
   * Enter the cookie's name in the input field and click "Find Cookie". The app will tell you if it found the cookie and display its value.

## Disclaimer

This solution relies on Streamlit's internal APIs (`_session_mgr`, `ScriptRunContext`). These APIs are not officially documented for this purpose and could change in future versions of Streamlit, which might break this functionality. The function is wrapped in a `try...except` block to prevent your app from crashing if such a change occurs.

## Acknowledgements

This work was inspired by and adapted from the insights of the Streamlit community and developers facing similar challenges.
