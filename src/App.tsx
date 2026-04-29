
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ErrorBoundary from "@/components/ErrorBoundary";
import Home from "@/pages/Home";
import Survey from "@/pages/Survey";
import Analysis from "@/pages/Analysis";

export default function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/survey" element={<Survey />} />
          <Route path="/analysis" element={<Analysis />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
}
