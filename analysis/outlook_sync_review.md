# Outlook Sync Script Review

## Résumé
Analyse du script Deno chargé de synchroniser les événements Outlook vers Supabase.

## Problèmes identifiés

1. **Absence de validation des variables d'environnement critiques.** Le script suppose que `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` et les identifiants Outlook sont toujours définis. En cas d'oubli de configuration, la fonction `createClient` recevra `undefined` et l'appel à l'API OAuth échouera de manière déroutante. Il est préférable de vérifier explicitement ces valeurs et de retourner une erreur explicite avant de poursuivre.
2. **Incohérence de fuseau horaire pour les dates d'événements.** L'en-tête `Prefer: outlook.timezone="Europe/Paris"` renvoie des chaînes sans décalage horaire (par ex. `2024-05-01T10:00:00.0000000`). `new Date()` interprète ces valeurs dans le fuseau horaire local du runtime (souvent UTC), ce qui décale les événements de +1/+2h. Il vaut mieux demander directement des dates en UTC ou utiliser le champ `timeZone` renvoyé pour effectuer une conversion robuste.
3. **Suppression trop agressive côté base de données.** La requête de suppression retire tous les événements Microsoft qui ne figurent pas dans la liste `externalIds`. Or, `calendarView` ne renvoie que les événements de la fenêtre 30j/90j. Les événements plus anciens sont supprimés à tort. De plus, lorsque `externalIds` est vide, tous les événements restants sont supprimés, même s'ils sont valides. Il faut filtrer la suppression sur la même plage temporelle (par ex. `start_at` entre `startISO` et `endISO`) et/ou éviter de lancer la suppression si la liste est vide.
4. **Pas de gestion de pagination Microsoft Graph.** L'appel `calendarView` est limité à `$top=250`. En cas de volume supérieur, `@odata.nextLink` n'est pas traité et les événements supplémentaires sont ignorés.
5. **Boucle d'upsert séquentielle.** Chaque événement est upserté dans une boucle `for` avec un `await` séquentiel, ce qui ralentit l'exécution. On peut regrouper les opérations (par ex. `Promise.all`) ou utiliser une RPC/batch côté Supabase pour optimiser.
6. **Manque de traçabilité du propriétaire.** Aucune vérification n'est effectuée sur le jeton transmis dans l'en-tête `Authorization`. Avec la clé `service_role`, un appel malveillant peut synchroniser n'importe quel `user_id`. Il faudrait valider le JWT via Supabase (`sb.auth.getUser`) ou limiter l'accès à un contexte sécurisé (Edge Function protégée).
7. **Gestion des erreurs d'upsert silencieuse.** Les appels Supabase `upsert` ne vérifient pas la valeur de retour; une erreur silencieuse pourrait passer inaperçue. Il est conseillé de capturer `error` et de journaliser ou interrompre la synchronisation si nécessaire.

## Suggestions supplémentaires

- Surveiller `@odata.deltaLink` pour implémenter une synchronisation incrémentale.
- Enrichir les logs en cas d'échec de rafraîchissement de token (HTTP status + payload).
- Documenter explicitement les colonnes `calendar_events` attendues (types, contraintes, etc.) pour faciliter la maintenance.
