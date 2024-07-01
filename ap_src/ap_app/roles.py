#@login_required
#def promote_team_member(request, id, user_id):
#    """Checks to see if user is the owner and renders the Setting page"""
#    team = Team.objects.get(id=id)
#    user_relation = Relationship.objects.get(team=id, user=request.user)
#    if user_relation.role.role != "Owner":
#        return redirect("dashboard")
#    target_user = User.objects.get(id=user_id)
#    all_pending_relations = Relationship.objects.filter(
#        team=id, status=Status.objects.get(status="Pending")
#    )
#    current_relationship = Relationship.objects.get(team=team, user=target_user)
#    if current_relationship.role == Role.objects.get(role="Member"):
#        current_relationship.role = Role.objects.get(role="Co-Owner")
#        current_relationship.save()
#
#    return redirect(team_settings, team.id)


#@login_required
#def demote_team_member(request, id, user_id):
#    """Checks to see if user is the owner and renders the Setting page"""
#    team = Team.objects.get(id=id)
#    user_relation = Relationship.objects.get(team=id, user=request.user)
#    if user_relation.role.role != "Owner":
#        return redirect("dashboard")
#    target_user = User.objects.get(id=user_id)
#    all_pending_relations = Relationship.objects.filter(
#        team=id, status=Status.objects.get(status="Pending")
#    )
#    current_relationship = Relationship.objects.get(team=team, user=target_user)
#    if current_relationship.role == Role.objects.get(role="Co-Owner"):
#        current_relationship.role = Role.objects.get(role="Member")
#        current_relationship.save()
#
#    return redirect(team_settings, team.id)
#
#@login_required
#def remove_team_member(request, id, user_id):
#    """Removes a member from a team."""
#    team = Team.objects.get(id=id)
#    user_relation = Relationship.objects.get(team=id, user=request.user)
#    if user_relation.role.role != "Owner":
#        return redirect("dashboard") #Checks if the user is the owner and redirects to the dashboard if they aren't
#    target_user = User.objects.get(id=user_id) #Gets the user to be removed
#    target_relation = Relationship.objects.get(team=team, user=target_user) #Gets the target's relationship to the team
#    target_relation.custom_delete() #Deletes the relationship from the team, removing the user
#
#    return redirect(team_settings, team.id) #Redirects user back to the settings page