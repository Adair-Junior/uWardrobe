# uWardrobe

uWardrobe is an AI-powered personal wardrobe assistant designed to help users choose outfits from clothes they already own.

## Project Status

🚧 Currently in development.

## MVP

The first version of uWardrobe will focus on:

- Digital wardrobe management
- Personal style preferences
- AI-powered outfit recommendations
- Weather and occasion awareness
- Voice interaction

## Technology Stack

### Backend
- Python
- FastAPI
- Pydantic
- pytest

### Mobile
- React Native
- Expo
- TypeScript

### Data & Services
- PostgreSQL / Supabase
- Supabase Auth
- Supabase Storage
- Open-Meteo

### AI
- Provider-independent AI architecture
- Gemini for initial cloud AI experiments
- Local AI experimentation where hardware permits

## Development Philosophy

uWardrobe is being built incrementally as both a real application and a software engineering learning project.

The project emphasizes:

- Understanding the architecture and code rather than blindly generating it
- Testing important application behavior
- Keeping AI services replaceable
- Validating AI-generated data before storing it
- Building with free and open-source tools or free service tiers where possible

## Current Progress

- [x] Product requirements defined
- [x] Initial architecture designed
- [x] Development environment configured
- [x] Python virtual environment created
- [x] FastAPI backend initialized
- [x] First API endpoint created
- [x] Interactive API documentation verified
- [x] First automated test created and passing
- [ ] Mobile application initialized
- [ ] Database connected
- [ ] Authentication implemented
- [ ] AI integration implemented

## Repository Structure

```text
uWardrobe/
├── backend/    # Python/FastAPI backend
├── mobile/     # React Native/Expo application
├── docs/       # Project documentation
└── README.md