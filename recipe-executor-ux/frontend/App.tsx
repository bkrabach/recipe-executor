import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import './App.css';

// Components
import ExecutionView from './components/ExecutionView';
import Header from './components/Header';
import RecipeDetail from './components/RecipeDetail';
import RecipeEditor from './components/RecipeEditor';
import RecipeList from './components/RecipeList';

function App() {
    return (
        <Router>
            <div className="app">
                <Header />
                <main className="container">
                    <Routes>
                        <Route path="/" element={<Navigate to="/recipes" replace />} />
                        <Route path="/recipes" element={<RecipeList />} />
                        <Route path="/recipes/new" element={<RecipeEditor />} />
                        <Route path="/recipes/:id" element={<RecipeDetail />} />
                        <Route path="/recipes/:id/edit" element={<RecipeEditor />} />
                        <Route path="/executions/:id" element={<ExecutionView />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;