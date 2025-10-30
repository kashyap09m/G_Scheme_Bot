/* --- Global Styles --- */

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f4f7f6; /* A light grey background */
  color: #333;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

/* --- Utility Classes --- */
.container {
  max-width: 1100px;
  margin: auto;
  padding: 0 20px;
  overflow: hidden;
}

/* --- Form Styles --- */
form {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-width: 500px;
  margin: 20px auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

form div {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

form label {
  font-weight: bold;
}

form input[type="text"],
form input[type="email"],
form input[type="password"],
form input[type="number"],
form select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box; /* Important for padding to not affect width */
}

form button {
  padding: 12px 20px;
  background-color: #004a99; /* A professional blue */
  color: white;
  font-size: 16px;
  font-weight: bold;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

form button:hover {
  background-color: #003366;
}

/* --- Link Styles --- */
a {
  color: #004a99;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
