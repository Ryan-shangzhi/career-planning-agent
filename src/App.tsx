
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "@/pages/Home";
import Survey from "@/pages/Survey";
import Analysis from "@/pages/Analysis";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/survey" element={<Survey />} />
        <Route path="/analysis" element={<Analysis />} />
      </Routes>
    </Router>
  );
}

