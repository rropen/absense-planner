#def team_invite(request, team_id, user_id, role):
#    find_team = Team.objects.get(id=team_id)
#    find_user = User.objects.get(id=user_id)
#    find_role = Role.objects.get(role=role)
#
#    test = Relationship.objects.filter(team=find_team)
#
#    # Boolean determines if viewer is in this team trying to invite others
#    user_acceptable = False
#    for rel in test:
#        if rel.user == request.user and str(rel.role) == "Owner":
#            user_acceptable = True
#            break
#
#    if str(request.user.id) != str(user_id) and user_acceptable:
#        Relationship.objects.create(
#            user=find_user,
#            team=find_team,
#            role=find_role,
#            status=Status.objects.get(status="Invited"),
#        )
#        return redirect(f"/teams/calendar/{find_team.id}")
#    # Else user is manipulating the URL making non-allowed invites - (Therefore doesn't create a relationship)
#
#    return redirect("dashboard")
#
#
#@login_required
#def view_invites(request):
#    all_invites = Relationship.objects.filter(
#        user=request.user, status=Status.objects.get(status="Invited")
#    )
#    return render(request, "teams/invites.html", {"invites": all_invites})