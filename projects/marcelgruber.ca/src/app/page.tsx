import Image from "next/image";

export default function Home() {
  return (
    <>
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-[#0a0a0a]/80 backdrop-blur-sm z-50 border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <a href="#hero" className="text-xl font-semibold text-white">
              Marcel Gruber
            </a>
            <div className="flex gap-8 text-sm">
              <a href="#about" className="text-gray-400 hover:text-white transition-colors">
                About
              </a>
              <a href="#services" className="text-gray-400 hover:text-white transition-colors">
                Services
              </a>
              <a href="#blog" className="text-gray-400 hover:text-white transition-colors">
                Blog
              </a>
              <a href="#contact" className="text-gray-400 hover:text-white transition-colors">
                Contact
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section id="hero" className="min-h-screen flex items-center pt-20">
        <div className="max-w-7xl mx-auto px-6 w-full">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <h1 className="text-6xl md:text-7xl font-bold text-white leading-tight">
                Marcel Gruber
              </h1>
              <p className="text-2xl md:text-3xl text-gray-300 leading-relaxed">
                I don't just talk about AI — I build with it. 11 years shipping enterprise web, 
                now making AI actually work for businesses.
              </p>
              <div className="pt-4">
                <a 
                  href="#contact" 
                  className="inline-block px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors"
                >
                  Let's work together
                </a>
              </div>
            </div>
            <div className="relative h-[500px] lg:h-[600px]">
              <Image
                src="/images/marcel-hero-clean.jpg"
                alt="Marcel Gruber speaking"
                fill
                className="object-cover rounded-2xl"
                priority
              />
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-32 border-t border-white/5">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-12">
            The story
          </h2>
          <div className="space-y-6 text-lg text-gray-300 leading-relaxed">
            <p>
              I've been building for the web since 2014. Started with enterprise .NET and Sitecore, 
              worked my way up from full-stack dev to architect. Shipped projects for Syncrude, 
              CFP Board, Cooley, CLIA, Annual Reviews, Rain. The kind of work where downtime costs 
              real money and migrations can't fail.
            </p>
            <p>
              I'm a 3x Sitecore Technology MVP (2023-2025) and currently an Architect at One North, 
              a TEKsystems company. But my real work happens through Luxica Consulting Corp, the 
              company I've been running for over 11 years.
            </p>
            <p>
              Here's what changed: AI isn't a trend anymore. It's infrastructure. And most businesses 
              have no idea how to use it. They're stuck in proof-of-concept hell, paying consultants 
              who've never shipped production code.
            </p>
            <p>
              I build agentic AI systems that actually work. AI assistants that handle real workflows. 
              AI-augmented processes that make businesses faster. Not demos. Not vaporware. Real systems, 
              in production, doing the work.
            </p>
            <p>
              Enterprise web taught me how to ship. AI gave me new tools. Calgary, Alberta is home base, 
              but I work with teams everywhere.
            </p>
            <p className="text-white font-medium pt-4">
              If you need someone who builds instead of theorizes, we should talk.
            </p>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-32 border-t border-white/5">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-16">
            What I do
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            {/* Service 1 */}
            <div className="space-y-4">
              <h3 className="text-2xl font-semibold text-white">
                Enterprise Web Architecture
              </h3>
              <p className="text-gray-300 leading-relaxed">
                Sitecore, .NET, headless CMS, DXP. I've been doing this for 11 years and earned 
                3x Sitecore Technology MVP recognition. I architect systems that scale, migrate 
                platforms without breaking things, and fix what others couldn't.
              </p>
              <p className="text-sm text-gray-400">
                Tech: Sitecore (10.x, XM Cloud, Content Hub, CDP, Personalize), .NET/C#, Next.js, 
                React, TypeScript, Azure
              </p>
            </div>

            {/* Service 2 */}
            <div className="space-y-4">
              <h3 className="text-2xl font-semibold text-white">
                WordPress Development & Rescue
              </h3>
              <p className="text-gray-300 leading-relaxed">
                Your WordPress site is slow, hacked, or stuck on ancient infrastructure. I migrate, 
                optimize, secure, and host properly. Cloudflare integration, performance tuning, 
                security hardening. The boring stuff that keeps businesses running.
              </p>
              <p className="text-sm text-gray-400">
                Tech: WordPress, PHP, Cloudflare, modern hosting, security best practices
              </p>
            </div>

            {/* Service 3 */}
            <div className="space-y-4">
              <h3 className="text-2xl font-semibold text-white">
                AI & Agentic Systems
              </h3>
              <p className="text-gray-300 leading-relaxed">
                This is where it gets interesting. I build and operate agentic AI assistants — 
                systems that actually do work, not just answer questions. AI consulting for businesses 
                that want results, not buzzwords. AI-augmented workflows that make teams faster.
              </p>
              <p className="text-sm text-gray-400">
                Tech: Python, LLM APIs, agentic frameworks, production AI systems
              </p>
            </div>

            {/* Service 4 */}
            <div className="space-y-4">
              <h3 className="text-2xl font-semibold text-white">
                SEO & Digital Strategy
              </h3>
              <p className="text-gray-300 leading-relaxed">
                Technical SEO, analytics implementation, competitive analysis. I find what's broken, 
                fix it, and measure the results. No snake oil, just data and execution.
              </p>
              <p className="text-sm text-gray-400">
                Tech: Google Analytics, Search Console, technical audits, schema markup
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Blog Section */}
      <section id="blog" className="py-32 border-t border-white/5">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-8">
            Writing
          </h2>
          <p className="text-xl text-gray-300 mb-8 leading-relaxed">
            I write about Sitecore, enterprise web development, and what I'm learning as I build 
            AI systems. Technical posts, lessons learned, the stuff I wish someone had written 
            when I was figuring it out.
          </p>
          <a 
            href="https://sitecore.marcelgruber.ca" 
            target="_blank" 
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 font-medium transition-colors"
          >
            Read the Sitecore blog
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </a>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-32 border-t border-white/5">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-12">
            Get in touch
          </h2>
          <div className="space-y-6 text-lg text-gray-300">
            <p className="text-xl leading-relaxed">
              Working on something interesting? Need someone who actually ships? Let's talk.
            </p>
            <div className="space-y-4 pt-8">
              <div>
                <span className="text-gray-400">Email:</span>{" "}
                <a 
                  href="mailto:marcel@luxc.ca" 
                  className="text-purple-400 hover:text-purple-300 transition-colors"
                >
                  marcel@luxc.ca
                </a>
              </div>
              <div>
                <span className="text-gray-400">LinkedIn:</span>{" "}
                <a 
                  href="https://linkedin.com/in/marcelgruber" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-purple-400 hover:text-purple-300 transition-colors"
                >
                  linkedin.com/in/marcelgruber
                </a>
              </div>
              <div>
                <span className="text-gray-400">Company:</span>{" "}
                <a 
                  href="https://luxicaconsultingcorp.com" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-purple-400 hover:text-purple-300 transition-colors"
                >
                  luxicaconsultingcorp.com
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-gray-400 text-sm">
            <p>© {new Date().getFullYear()} Marcel Gruber. Built with Next.js.</p>
            <p>Calgary, Alberta, Canada</p>
          </div>
        </div>
      </footer>
    </>
  );
}
