from sqlalchemy.orm import Session
from app.db.models import (
    CharacterArchetype, GameGenre, InterviewQuestion, 
    ProductionConstraint, DesignerProfile, StatSystem, SkillTree
)

def seed_data(db: Session) -> None:
    if db.query(GameGenre).count() > 0:
        return

    # 1. Game Genres
    genres = [
        GameGenre(name="Action RPG", description="Fast-paced combat with character progression and loot systems."),
        GameGenre(name="Narrative Adventure", description="Story-centric games focused on exploration and choice."),
        GameGenre(name="Tactical Shooter", description="High-stakes combat requiring strategy and teamwork."),
        GameGenre(name="Survival Horror", description="Focuses on resource management and psychological tension."),
        GameGenre(name="MMORPG", description="Persistent worlds with thousands of players and complex economies."),
        GameGenre(name="Soulslike", description="High difficulty, stamina-based combat with environmental storytelling."),
    ]
    db.add_all(genres)
    db.flush() # Get IDs

    # 2. Character Archetypes
    archetypes = [
        CharacterArchetype(name="Tank", design_notes="High survivability, crowd control, and damage mitigation."),
        CharacterArchetype(name="Rogue", design_notes="High burst damage, stealth, and mobility utility."),
        CharacterArchetype(name="Glass Cannon Mage", design_notes="Extreme area-of-effect damage but very low health."),
        CharacterArchetype(name="Support Cleric", design_notes="Healing, buffing, and defensive utility for the team."),
        CharacterArchetype(name="Berserker", design_notes="High damage that increases as health decreases."),
        CharacterArchetype(name="Sniper", design_notes="Long-range precision with specialized scouting tools."),
    ]
    db.add_all(archetypes)
    db.flush()

    # 3. Stat Systems
    db.add_all([
        StatSystem(system_name="The Core Triad", primary_stats={"Strength": "Physical Power", "Agility": "Speed/Crit", "Intellect": "Mana/Spell Power"}),
        StatSystem(system_name="Souls-Inspired", primary_stats={"Vigor": "Health", "Endurance": "Stamina", "Faith": "Miracles"}),
        StatSystem(system_name="Cybernetic Mods", primary_stats={"Neural": "Hacking", "Biotic": "Ability Spans", "Chrome": "Armor Block"}),
    ])

    # 4. Skill Trees
    tank = db.query(CharacterArchetype).filter_by(name="Tank").first()
    rogue = db.query(CharacterArchetype).filter_by(name="Rogue").first()
    if tank:
        db.add(SkillTree(archetype_id=tank.id, name="Iron Bastion", nodes={"Shield Bash": "Level 1", "Unstoppable Force": "Level 10", "Last Stand": "Level 25"}))
    if rogue:
        db.add(SkillTree(archetype_id=rogue.id, name="Shadow Step", nodes={"Backstab": "Level 1", "Vanishing Act": "Level 12", "Eviscerate": "Level 30"}))

    # 5. Production Constraints
    db.add_all([
        ProductionConstraint(project_name="Odyssey Alpha", platform="Mobile", memory_budget_mb=1024, timeline_weeks=52, max_asset_polycount=15000),
        ProductionConstraint(project_name="Skyrim 2.0", platform="PC/PS5/Xbox", memory_budget_mb=8192, timeline_weeks=156, max_asset_polycount=85000),
        ProductionConstraint(project_name="Pixel Puncher", platform="Nintendo Switch", memory_budget_mb=2048, timeline_weeks=26, max_asset_polycount=25000),
    ])

    # 6. Designer Profiles
    db.add_all([
        DesignerProfile(name="Yuvraj Jain", experience_years=10, specialization="Combat Systems", strengths={"AI Behavior": 9, "Math": 8, "VFX Coordination": 7}),
        DesignerProfile(name="Sarah Connor", experience_years=4, specialization="World Building", strengths={"Narrative Design": 9, "Lore": 10, "Quest Flow": 8}),
        DesignerProfile(name="Ken Masters", experience_years=15, specialization="Economy Design", strengths={"Balancing": 10, "Spreadsheets": 10, "Monetization": 9}),
    ])

    # 7. Interview Questions (The Bank)
    db.add_all([
        # Character Design Category
        InterviewQuestion(category="Character Design", difficulty="Mid", expected_competency="Visual Readability", question_text="How do you ensure a fast-moving rogue stays readable in a chaotic 10-player match?"),
        InterviewQuestion(category="Character Design", difficulty="Senior", expected_competency="Archetype Breaking", question_text="Propose a 'Tank' ability that doesn't use a shield or high armor but still protects the team."),
        
        # Production Category
        InterviewQuestion(category="Production", difficulty="Junior", expected_competency="Resource Management", question_text="A character asset is 10k over the polycount budget. What is your process for optimization?"),
        InterviewQuestion(category="Production", difficulty="Lead", expected_competency="Timeline Tradeoffs", question_text="If we are 2 weeks behind, which 'juice' features do you cut first without ruining the character feel?"),
        
        # Narrative Category
        InterviewQuestion(category="Narrative", difficulty="Senior", expected_competency="Environmental Storytelling", question_text="How would you design a character whose backstory is told almost exclusively through their idle animations and gear?"),
    ])

    db.commit()
