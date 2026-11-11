# --- Étape 1 : construire les fichiers statiques ---
FROM node:22-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# --- Étape 2 : image finale, uniquement nginx et le résultat ---
# Variante « unprivileged » : nginx ne tourne pas en root et écoute sur 8080.
FROM nginxinc/nginx-unprivileged:stable-alpine

COPY nginx-securite.conf /etc/nginx/snippets/securite.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080
