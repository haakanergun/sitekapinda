import Image from "next/image";

const menu = [
  {
    number: "01",
    title: "Charcoal köfte",
    detail: "Hand-shaped beef, fire-roasted pepper, bulgur pilaf, strained yoghurt.",
    note: "House signature",
  },
  {
    number: "02",
    title: "Market vegetables",
    detail: "Seasonal greens, burnt lemon, toasted seeds, warm herb dressing.",
    note: "Changes weekly",
  },
  {
    number: "03",
    title: "Shared table",
    detail: "A generous chef-selected spread for the whole table, served family style.",
    note: "For 2 or more",
  },
];

export default function Home() {
  return (
    <main>
      <div className="demo-strip">
        <span>Fictional customer preview</span>
        <span>Built and hosted with the Codex Sites extension</span>
      </div>

      <header className="site-header">
        <a className="wordmark" href="#top" aria-label="Sedirra home">Sedirra</a>
        <nav aria-label="Primary navigation">
          <a href="#menu">Menu</a>
          <a href="#story">Our table</a>
          <a href="#private">Private dining</a>
          <a href="#visit">Visit</a>
        </nav>
        <a className="button button-copper header-cta" href="#review">Review this demo</a>
      </header>

      <section className="hero" id="top">
        <Image
          src="/sedirra-hero.png"
          alt="A warm fictional Istanbul restaurant interior with a Turkish köfte plate"
          fill
          priority
          sizes="100vw"
          className="hero-image"
        />
        <div className="hero-shade" />
        <div className="hero-content">
          <p className="eyebrow">Istanbul · neighborhood kitchen</p>
          <h1>A neighborhood table, thoughtfully made.</h1>
          <p className="hero-copy">Seasonal Turkish cooking, charcoal-fired and made to share.</p>
          <div className="hero-actions">
            <a className="button button-outline" href="#menu">View the menu</a>
            <a className="button button-copper" href="#visit">Plan a visit</a>
          </div>
        </div>
        <p className="hero-caption">Concept imagery created for this rights-safe demo.</p>
      </section>

      <section className="principles" aria-label="Restaurant highlights">
        <div><span>01</span><strong>Köfte &amp; bulgur</strong></div>
        <div><span>02</span><strong>Charcoal &amp; greens</strong></div>
        <div><span>03</span><strong>Seasonal plates</strong></div>
      </section>

      <section className="menu-section" id="menu">
        <div className="section-heading">
          <div>
            <p className="eyebrow copper">From the kitchen</p>
            <h2>Simple food. Deeply considered.</h2>
          </div>
          <p>Built around what is best today: honest ingredients, open-fire cooking, and dishes that invite one more plate to the table.</p>
        </div>
        <div className="menu-grid">
          {menu.map((item) => (
            <article className="menu-card" key={item.number}>
              <div className="menu-card-top"><span>{item.number}</span><span>{item.note}</span></div>
              <h3>{item.title}</h3>
              <p>{item.detail}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="story-section" id="story">
        <div className="story-image-wrap">
          <Image
            src="/sedirra-hero.png"
            alt="The fictional Sedirra dining room"
            fill
            sizes="(max-width: 800px) 100vw, 52vw"
            className="story-image"
          />
        </div>
        <div className="story-copy">
          <p className="eyebrow copper">Our table</p>
          <h2>Made for lingering.</h2>
          <p className="story-lead">Sedirra imagines the kind of place where lunch becomes afternoon and every table feels like the best seat in the room.</p>
          <p>This is a fictional restaurant concept created to demonstrate how a customer can review a working first version before committing to a domain or public launch.</p>
          <a href="#review" className="text-link">How the review works <span>→</span></a>
        </div>
      </section>

      <section className="private-section" id="private">
        <p className="eyebrow">Private dining</p>
        <h2>One table. Your occasion.</h2>
        <p>A quieter setting, a menu shaped around the group, and service with room for the evening to unfold.</p>
        <a href="#review" className="button button-cream">Request a revision</a>
      </section>

      <section className="visit-section" id="visit">
        <div>
          <p className="eyebrow copper">Visit</p>
          <h2>Your next neighborhood favorite.</h2>
          <p className="visit-note">Concept location: Kadıköy, Istanbul. No real address, phone number, or booking system is connected to this demo.</p>
        </div>
        <dl>
          <div><dt>Tuesday–Thursday</dt><dd>12:00–22:30</dd></div>
          <div><dt>Friday–Saturday</dt><dd>12:00–23:30</dd></div>
          <div><dt>Sunday</dt><dd>12:00–21:30</dd></div>
          <div><dt>Monday</dt><dd>Closed</dd></div>
        </dl>
      </section>

      <section className="review-section" id="review">
        <span className="review-kicker">Customer review link</span>
        <h2>This is the first version—not the final launch.</h2>
        <p>The customer opens this working Sites demo, comments on copy, imagery, layout, and calls to action, then explicitly approves the version that can move to a custom domain.</p>
        <div className="review-flow" aria-label="Review workflow">
          <span>Demo link</span><i>→</i><span>Customer revisions</span><i>→</i><span>Approval</span><i>→</i><span>Custom domain</span>
        </div>
      </section>

      <footer>
        <span className="wordmark">Sedirra</span>
        <span>Fictional concept · Sites demo</span>
        <span>Prepared by SiteKapında</span>
      </footer>
    </main>
  );
}
