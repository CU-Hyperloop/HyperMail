// src/main.tsx
import ReactDOM from 'react-dom/client'; //provides necessary components to render React components as DOM (Document Object Model)
import App from './App'; //root component of react application

//render App as DOM
ReactDOM.createRoot(document.getElementById('root')!).render(<App />);