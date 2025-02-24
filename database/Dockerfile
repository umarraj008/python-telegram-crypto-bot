FROM postgres:15

# Set environment variables for default database
ENV POSTGRES_USER=your_user
ENV POSTGRES_PASSWORD=your_password
ENV POSTGRES_DB=telegram_db

# Copy initialization SQL script (if needed)
COPY init.sql /docker-entrypoint-initdb.d/

EXPOSE 5432